module.exports = {
  apps: [
    {
      name: 'server',
      script: './server.py',
      interpreter: './venv/bin/python',
      watch: false,  // Optional: Enable if you want pm2 to watch for file changes
      autorestart: true,  // Optional: Enable auto-restart if the app crashes
    },
  ],
};
