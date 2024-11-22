module.exports = {
  apps: [
    {
      name: 'server',
      script: './server.py',
      interpreter: './venv/bin/python',
      watch: false,  // Optional: Enable if you want pm2 to watch for file changes
      autorestart: true,  // Optional: Enable auto-restart if the app crashes
    },
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
      args: ['-A', 'server.celery', 'worker', '--concurrency=3', '--loglevel=info'],
      interpreter: 'none',  // Don't use any interpreter since celery is executable
      autorestart: true
    }
  ],
};
