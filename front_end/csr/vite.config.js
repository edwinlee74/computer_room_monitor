import { defineConfig } from 'vite'

export default defineConfig({
     server: {
         host: '0.0.0.0',
         port: "5000",
         open: false,
         proxy: {
            "^/socket.io/": {
              target: 'http://192.168.10.86:8000/',
              changeOrigin: true,
              secure: false,
              rewrite: (path) => path.replace(/^\/socket.io/, ""),
            },
          },
        },
     headers: {
        'Access-Control-Allow-Origin': '*',
     }
})
