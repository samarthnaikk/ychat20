const pool = require('../src/config/database');
const fs = require('fs');
const path = require('path');

async function initDatabase() {
  try {
    console.log('Initializing database...');
    
    const schemaSQL = fs.readFileSync(
      path.join(__dirname, 'schema.sql'),
      'utf8'
    );
    
    await pool.query(schemaSQL);
    
    console.log('Database initialized successfully!');
    process.exit(0);
  } catch (error) {
    console.error('Error initializing database:', error);
    process.exit(1);
  }
}

initDatabase();
