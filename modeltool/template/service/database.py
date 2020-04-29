import time
import logging
import pymysql


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_current_date():
    current_time = time.strftime("%Y%m%d%H%M%S", time.gmtime())
    return int(current_time)


def connect_to_db(db_user, db_password, db_url, db_schema):
    try:
        database_engine = pymysql.connect(
            user=db_user, password=db_password, host=db_url, db=db_schema
        )
        logging.info("created database engine")
        cursor = database_engine.cursor()
        return database_engine, cursor
    except Exception as e:
        logging.error(e)


def insert_model_stats(response_time, model_file, predictions, database_engine, cursor, lambda_name):
    run_ts = get_current_date()
    logger.info(run_ts)
    insert_query = """
    INSERT INTO run_time_stats (
    LAMBDA_NM,
    RUN_TS,
    RESULT,
    ML_RUN_TM,
    MODEL_NM
    ) VALUES (%s, %s, %s, %s, %s)
    """
    params = (
        lambda_name,
        run_ts,
        predictions,
        response_time,
        model_file,
    )
    try:
        logger.info('starting insert')
        cursor.execute(insert_query, params)
        logger.info('Insert success')
        database_engine.commit()
    except Exception as e:
        logger.error(e)
    return
