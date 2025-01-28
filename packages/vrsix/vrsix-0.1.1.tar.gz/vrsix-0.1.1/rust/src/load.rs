use crate::sqlite::{get_db_connection, setup_db, DbRow};
use crate::{FiletypeError, SqliteFileError, VcfError, VrsixDbError};
use futures::TryStreamExt;
use log::{error, info};
use noodles_bgzf::r#async::Reader as BgzfReader;
use noodles_vcf::{
    self as vcf,
    r#async::io::Reader as VcfReader,
    variant::record::info::{self, field::Value as InfoValue},
};
use pyo3::{exceptions, prelude::*};
use sqlx::{error::DatabaseError, sqlite::SqliteError, SqlitePool};
use std::path::PathBuf;
use std::time::Instant;
use tokio::{
    fs::File as TkFile,
    io::{AsyncBufRead, BufReader},
};

async fn load_allele(db_row: DbRow, pool: &SqlitePool) -> Result<(), Box<dyn std::error::Error>> {
    let mut conn = pool.acquire().await?;
    let result =
        sqlx::query("INSERT INTO vrs_locations (vrs_id, chr, pos, uri_id) VALUES (?, ?, ?, ?);")
            .bind(db_row.vrs_id)
            .bind(db_row.chr)
            .bind(db_row.pos)
            .bind(db_row.uri_id)
            .execute(&mut *conn)
            .await;
    if let Err(err) = result {
        if let Some(db_error) = err.as_database_error() {
            if let Some(sqlite_error) = db_error.try_downcast_ref::<SqliteError>() {
                if sqlite_error
                    .code()
                    .map(|code| code == "2067")
                    .unwrap_or(false)
                {
                    error!("duplicate");
                    return Ok(());
                }
            }
        }
        return Err(err.into());
    }
    Ok(())
}

fn get_vrs_ids(info: vcf::record::Info, header: &vcf::Header) -> Result<Vec<String>, PyErr> {
    if let Some(Ok(Some(InfoValue::Array(array)))) = info.get(header, "VRS_Allele_IDs") {
        if let info::field::value::Array::String(array_elements) = array {
            let vec = array_elements
                .iter()
                .map(|cow_str| cow_str.unwrap().unwrap_or_default().to_string())
                .collect();
            return Ok(vec);
        } else {
            error!("Unable to unpack `{:?}` as an array of values", array);
            Err(VcfError::new_err("expected string array variant"))
        }
    } else {
        error!(
            "Unable to unpack VRS_Allele_IDs from info fields: {:?}. Are annotations available?",
            info
        );
        Err(VcfError::new_err("Expected Array variant"))
    }
}

async fn get_reader(
    vcf_path: PathBuf,
) -> Result<VcfReader<Box<dyn tokio::io::AsyncBufRead + Unpin + Send>>, PyErr> {
    let file = TkFile::open(vcf_path.clone()).await.map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyOSError, _>(format!("Failed to open file: {}", e))
    })?;
    let ext = vcf_path.extension().and_then(|ext| ext.to_str());
    match ext {
        Some("gz") => {
            let reader = Box::new(BgzfReader::new(file)) as Box<dyn AsyncBufRead + Unpin + Send>;
            Ok(VcfReader::new(reader))
        }
        Some("vcf") => {
            let reader = Box::new(BufReader::new(file)) as Box<dyn AsyncBufRead + Unpin + Send>;
            Ok(VcfReader::new(reader))
        }
        _ => {
            error!(
                "Unexpected file extension `{:?}` for input file `{:?}`",
                ext, vcf_path
            );
            Err(PyErr::new::<FiletypeError, _>(format!(
                "Unsupported file extension: {:?}",
                ext
            )))
        }
    }
}

async fn load_file_uri(uri: &str, pool: &SqlitePool) -> Result<i64, Box<dyn std::error::Error>> {
    let mut conn = pool.acquire().await?;

    let insert_result = sqlx::query("INSERT OR IGNORE INTO file_uris (uri) VALUES (?);")
        .bind(uri)
        .execute(&mut *conn)
        .await?;
    if insert_result.rows_affected() > 0 {
        Ok(insert_result.last_insert_rowid())
    } else {
        let row_id: (i64,) = sqlx::query_as("SELECT id FROM file_uris WHERE uri = ?;")
            .bind(uri)
            .fetch_one(&mut *conn)
            .await?;
        Ok(row_id.0)
    }
}

pub async fn load_vcf(vcf_path: PathBuf, db_url: &str, uri: String) -> PyResult<()> {
    let start = Instant::now();

    if !vcf_path.exists() || !vcf_path.is_file() {
        error!("Input file `{:?}` does not appear to exist", vcf_path);
        return Err(exceptions::PyFileNotFoundError::new_err(
            "Input path does not lead to an existing file",
        ));
    }

    setup_db(db_url).await.map_err(|_| {
        error!("Unable to open input file `{:?}` into sqlite", db_url);
        SqliteFileError::new_err("Unable to open DB file -- is it a valid sqlite file?")
    })?;

    let mut reader = get_reader(vcf_path).await?;
    let header = reader.read_header().await?;

    let mut records = reader.records();

    let db_pool = get_db_connection(db_url).await.map_err(|e| {
        error!("DB connection failed: {}", e);
        VrsixDbError::new_err(format!("Failed database connection/call: {}", e))
    })?;

    let uri_id = load_file_uri(&uri, &db_pool)
        .await
        .map_err(|e| VrsixDbError::new_err(format!("Failed to insert file URI `{uri}`: {e}")))?;

    while let Some(record) = records.try_next().await? {
        let vrs_ids = get_vrs_ids(record.info(), &header)?;
        let chrom = record.reference_sequence_name();
        let pos = record.variant_start().unwrap()?.get();

        for vrs_id in vrs_ids {
            let row = DbRow {
                vrs_id: vrs_id
                    .strip_prefix("ga4gh:VA.")
                    .unwrap_or(&vrs_id)
                    .to_string(),
                chr: chrom.to_string(),
                pos: pos.try_into().unwrap(),
                uri_id,
            };
            load_allele(row, &db_pool).await.map_err(|e| {
                error!("Failed to load row {:?}", e);
                VrsixDbError::new_err(format!("Failed to load row: {}", e))
            })?;
        }
    }

    let duration = start.elapsed();
    info!("Time taken: {:?}", duration);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::NamedTempFile;

    #[tokio::test]
    async fn test_load_file_uri() {
        let temp_file = NamedTempFile::new().expect("Failed to create temp file");
        let db_url = format!("sqlite://{}", temp_file.path().to_str().unwrap());
        crate::sqlite::setup_db(&db_url).await.unwrap();
        let db_pool = get_db_connection(&db_url).await.unwrap();
        let uri_id = load_file_uri("file:///arbitrary/file/location.vcf", &db_pool)
            .await
            .unwrap();
        assert!(uri_id == 1);
    }
}
