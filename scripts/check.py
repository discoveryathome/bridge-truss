import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from truss.verify import verify
p=argparse.ArgumentParser(); p.add_argument('candidate'); p.add_argument('--output'); args=p.parse_args()
try:
 report=verify(json.loads(Path(args.candidate).read_text()))
 if args.output: Path(args.output).write_text(json.dumps(report,indent=2)+'\n')
 print(f"PASS {report['case']} {report['profile']} mass={report['primary']['mass_lbm']:.9f} lbm; both solvers agree")
except (ValueError,KeyError,TypeError) as e:
 print('FAIL',e,file=sys.stderr); sys.exit(1)
