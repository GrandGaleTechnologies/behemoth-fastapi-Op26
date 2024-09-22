import subprocess


def run_fastapi_server():
    try:
        # This runs the "fastapi dev" command
        subprocess.run(["fastapi", "dev"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to run FastAPI server: {e}")


if __name__ == "__main__":
    run_fastapi_server()
