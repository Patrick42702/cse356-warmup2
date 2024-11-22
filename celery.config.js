module.exports = {
  apps: [
    {
      name: 'flower',
      script: './venv/bin/celery',
      args: ['-A', 'server.celery', 'flower'],
      interpreter: 'none',  // Don't use any interpreter since celery is executable
      autorestart: true
    },
    {
      name: 'worker',
      script: './venv/bin/celery',
      args: ['-A', 'server.celery', 'worker', '--concurrency=6', '--loglevel=info'],
      interpreter: 'none',  // Don't use any interpreter since celery is executable
      autorestart: true
    }
  ],
};
