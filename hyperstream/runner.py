import os
import uvicorn
from uvicorn import Server

if __name__ == '__main__':                
        uvicorn.run(
                "main:hs",
                host="127.0.0.1",
                port=8083,
                reload='True',
                factory=True,    
                app_dir = os.getcwd(),
                reload_dirs=[os.getcwd()],
                )