import pathlib
import uuid


class Log:
  def __init__(self, file_path: str):
    self.file_path = file_path
    pathlib.Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)

  def print(self, message: str):
    print(message)
    with open(self.file_path, "a") as f:
      f.write(str(message) + "\n")


def get_log(base_dir: pathlib.Path):
  return Log(base_dir / f"{uuid.uuid4()}/log.txt")
