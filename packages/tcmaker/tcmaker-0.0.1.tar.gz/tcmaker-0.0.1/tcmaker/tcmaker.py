import random
import re
import os

class tcmaker:
    def __init__(self):
        self.dicVar = {}
        self.variables = {}
        self.chkUnique = set()
        
    def randval(self, start, end):
        if isinstance(start, int) and isinstance(end, int):
            return random.randrange(start, end+1)
        else:
            return random.uniform(start, end+1e-10)

    def convert_value(self, value):               
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value     

    def eval_value(self, value):
        return eval(value, {}, self.dicVar)
 
    def is_number(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def parse_format_file(self, file_path):
        with open(file_path, 'r') as f:
            data = f.read()
        
        var_section = re.search(r'\[Var\](.*?)\[Format\]', data, re.S).group(1).strip()
        format_section = re.search(r'\[Format\](.*)', data, re.S).group(1).strip()
        
        for line in var_section.split('\n'):
            name, range_str = line.split(':')
            min_val, max_val = range_str.strip().split('~')
            self.variables[name.strip()] = (self.convert_value(min_val), self.convert_value(max_val))
        
        return self.variables, format_section
    
    def generate_value(self, var_name):
        min_val, max_val = self.variables[var_name]
        
        if not self.is_number(min_val):
            min_val = eval(min_val, {}, self.dicVar)
        if not self.is_number(max_val):
            max_val = eval(max_val, {}, self.dicVar)
        self.dicVar[var_name] = self.randval(min_val, max_val)
        return self.dicVar[var_name]
    
    def generate_unique_value(self, var_name):
        min_val, max_val = self.variables[var_name]
        
        if not self.is_number(min_val):
            min_val = eval(min_val, {}, self.dicVar)
        if not self.is_number(max_val):
            max_val = eval(max_val, {}, self.dicVar)
        
        prev = len(self.chkUnique)
        while True:
            temp = self.randval(min_val, max_val)
            self.chkUnique.add(temp)
            after = len(self.chkUnique)
            if prev != after:
                break
        return temp
    
    def process_format(self, format_section):
        output = []
        for line in format_section.split('\n'):
            if line.startswith('drept'):
                match = re.match(r"drept\(([a-zA-Z0-9\+\-\*/\(\)]+),\s*([a-zA-Z0-9\+\-\*/\(\)]+),\s*'([^']+)'\)", line, re.DOTALL)
                if match:
                    repeat_count, var_name, delimiter = match.groups()
                    repeat_count = self.eval_value(repeat_count)
                    values = [str(self.generate_unique_value(var_name)) for _ in range(repeat_count)]
                    delimiter = delimiter.replace("\\n", "\n")
                    output.append(delimiter.join(values))
            elif line.startswith('rept'):
                match = re.match(r"rept\(([a-zA-Z0-9\+\-\*/\(\)]+),\s*([a-zA-Z0-9\+\-\*/\(\)]+),\s*'([^']+)'\)", line, re.DOTALL)
                if match:
                    repeat_count, var_name, delimiter = match.groups()
                    repeat_count = self.eval_value(repeat_count)
                    values = [str(self.generate_value(var_name)) for _ in range(repeat_count)]
                    delimiter = delimiter.replace("\\n", "\n")
                    output.append(delimiter.join(values))
            else:
                for var_name in self.variables:
                    if var_name in line:
                        line = line.replace(var_name, str(self.generate_value(var_name)))
                    
                output.append(line)
        return '\n'.join(output)
    
    def make_output(self, input_file, output_file, run_file, terminal):
        if terminal=="PowerShell":
          cmd=f"type {input_file} | python3 {run_file} > {output_file}"
        else:
          cmd=f"python3 {run_file} < {input_file} > {output_file}"
          
        print(cmd)
        os.system(cmd)
      
    def generate(self, format_file, input_file, output_file, run_file, terminal ):
        self.variables, format_section = self.parse_format_file(format_file)
        result = self.process_format(format_section)
        f=open(input_file, 'w')
        f.write(result)
        f.close()
        self.make_output(input_file, output_file, run_file, terminal)
        
if __name__ == '__main__':
    tcm = tcmaker()
    format_file = 'format.txt'
    input_file = f'test.in'
    output_file = f'test.out'
    run_file = f'solve.py'
    terminal = 'PowerShell'
    tcm.generate(format_file, input_file, output_file, run_file, terminal)
    