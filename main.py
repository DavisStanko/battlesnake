from server import run_server
import functions
# import functions2

def main():
  run_server({
      "info": functions.info,
      "start": functions.start,
      "move": functions.move,
      "end": functions.end

      # "info": functions2.info,
      # "start": functions2.start,
      # "move": functions2.move,
      # "end": functions2.end
  })


if __name__ == "__main__":
  main()
