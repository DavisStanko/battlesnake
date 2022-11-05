from server import run_server
import functions

def main():
  run_server({
      "info": functions.info,
      "start": functions.start,
      "move": functions.move,
      "end": functions.end
  })


if __name__ == "__main__":
  main()
