from airflow.operators.python_operator import PythonOperator
from airflow.models import DAG
from datetime import datetime, timedelta
import airflow
import os


'''
The airflow scheduler generates about 1 gig of logs per day.
With only only 50 gigs avaliable on the dev server this can crash
the airflow instance if it runs unchecked.  This dag removes 
scheduler logs (none critical or helpful for debugging) that are
> 24 hours old.
'''

def clean_up():
    ts = datetime.now() + timedelta(hours=-24)
    yesterday = ts.strftime('%Y-%m-%d')
    log_dir_path = os.path.join(os.environ['AIRFLOW_HOME'], 'logs', 'scheduler', yesterday)

    files = os.listdir(log_dir_path)
    for file in files:
        rip_log = os.path.join(log_dir_path, file)
        os.remove(rip_log)
        print('log deleted:{}'.format(rip_log))
    else:
        os.removedirs(log_dir_path)
        print('folder removed: {}'.format(log_dir_path))


default_args = {
    'owner': 'komodo',
    'start_date': airflow.utils.dates.days_ago(1)
}


dag = DAG(
    dag_id='scheduler_log_cleanup',
    default_args=default_args,
    schedule_interval='0 10 * * *',
    max_active_runs=1
  )

remove_logs = PythonOperator(
            task_id='remove_scheduler_logs',
            python_callable=clean_up,
            dag=dag
    )