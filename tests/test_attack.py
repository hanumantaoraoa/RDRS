import os
from pathlib import Path
sandbox = Path('data/sandbox'); sandbox.mkdir(parents=True, exist_ok=True)
for i in range(50): (sandbox / f'file_{i}.txt').write_text('normal document content')
for f in list(sandbox.glob('*.txt')):
       f.write_bytes(os.urandom(20000))
       f.rename(f.with_suffix('.locked'))
       print('[*] Safe attack simulation complete.')