// vue.config.js
module.exports = {
    lintOnSave: false,
    devServer: {
        // proxy: 'https://localhost/',
        // port: 5000,     
        proxy: 'http://127.0.0.1:5000/api',  
        // proxy: 'http://localhost:8080',        
      headers: { "Access-Control-Allow-Origin": "*" }
    }
}