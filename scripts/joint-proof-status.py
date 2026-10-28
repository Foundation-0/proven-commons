#!/usr/bin/env python3
"""Report recorded joint-proof coverage without running Lean or contacting upstream."""
import argparse
from collections import defaultdict
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def inventory(state, audit):
    included = [r for r in state['repos'] if r.get('state') == 'included']
    owners = defaultdict(set)
    for rec in included:
        for namespace in rec.get('proof_namespaces', []):
            owners[namespace].add(rec['repo'])
    rows = []
    for rec in included:
        proof_libs = [lib for lib in rec.get('libs', []) if lib['kind'] == 'proofs']
        if not proof_libs:
            continue
        evidence = audit.get('packages', {}).get(rec['package'], {})
        pinned_audit = (audit.get('toolchain') == state.get('toolchain') and
                        evidence.get('rev') == rec.get('rev'))
        collisions = {name: sorted(owners[name] - {rec['repo']})
                      for name in rec.get('proof_namespaces', [])
                      if len(owners[name]) > 1}
        admitted = rec.get('joint_proofs') is True
        rows.append({'repository': rec['repo'], 'pin': rec['rev'],
                     'proof_roots': [root for lib in proof_libs for root in lib['roots']],
                     'jointly_admitted_by_sync': admitted,
                     'audit_matches_pin_and_toolchain': pinned_audit,
                     'shared_module_namespaces': collisions,
                     'sync_note': rec.get('joint_note'),
                     'remaining': ([] if admitted else ['upstream namespace/declaration integration and successful joint build'])
                                  + ([] if not collisions else ['shared module namespaces remain in the recorded inventory'])
                                  + ([] if pinned_audit else ['fresh audit at this pin and toolchain'])})
    pending = [r['repository'] for r in rows if r['remaining']]
    return {'toolchain': state['toolchain'], 'inventory_sync_date': state.get('synced'),
            'proof_packages': len(rows), 'jointly_admitted': sum(r['jointly_admitted_by_sync'] for r in rows),
            'pending_repositories': pending, 'recorded_coverage_complete': not pending,
            'evidence_limit': 'Recorded metadata only. This command does not compile Lean, detect declaration-name clashes, or establish upstream completion.',
            'packages': rows}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--require-complete', action='store_true', help='exit 1 if recorded coverage is incomplete')
    args = ap.parse_args()
    result = inventory(json.loads((ROOT/'repos.json').read_text()), json.loads((ROOT/'audit.json').read_text()))
    print(json.dumps(result, indent=2, sort_keys=True))
    return int(args.require_complete and not result['recorded_coverage_complete'])


if __name__ == '__main__':
    raise SystemExit(main())
