import tcmaker

start_n = 1    # 데이터 시작 번호
end_n = 1     # 데이터 끝 번호

for i in range(start_n, end_n+1):
  format_file = 'format.txt'        # 데이터 형식 지정 파일명
  input_file = f'test{i:02d}.in'    # 만들 입력 파일명
  output_file = f'test{i:02d}.out'  # 만들 출력 파일명
  run_file = 'solve.py'             # 정답 코드 파일명
  terminal = 'PowerShell'           # 터미널 종류(PowerShell 또는 아무거나)

  tcm = tcmaker.tcmaker()
  tcm.generate(format_file, input_file, output_file, run_file, terminal)