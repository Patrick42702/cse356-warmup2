module.exports = {
  apps: [
    {
      name: 'flower',
      script: './venv/bin/celery',
      args: ['-A', 'bp.celery_worker.app', 'flower'],
      interpreter: 'none',  // Don't use any interpreter since celery is executable
      autorestart: true
    },
    {
      name: 'worker',
      script: './venv/bin/celery',
      args: ['-A', 'bp.celery_worker.app', 'worker', '--concurrency=2', '--loglevel=info'],
      interpreter: 'none',  // Don't use any interpreter since celery is executable
      autorestart: true
    }
  ],
};
