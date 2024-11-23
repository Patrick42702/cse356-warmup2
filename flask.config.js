module.exports = {
  apps: [
    {
      name: 'server',
      script: './venv/bin/gunicorn',
      args: 'server:app --bind 127.0.0.1:5050 --workers 4',
      interpreter: 'none',  // Prevent PM2 from using another interpreter since Gunicorn is executable
      watch: false,         // Optional: Enable if you want pm2 to watch for file changes
      autorestart: true,    // Optional: Restart app if it crashes
    },
  ],
};
