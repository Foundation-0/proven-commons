import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('joint_status', Path(__file__).with_name('joint-proof-status.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def package(name, namespace, admitted=False):
    return {'repo': name, 'package': name, 'state': 'included', 'rev': 'a'*40,
            'libs':[{'kind':'proofs','roots':[namespace]}],
            'proof_namespaces':[namespace], 'joint_proofs':admitted}


class CoverageTests(unittest.TestCase):
    def check_state(self, packages):
        state={'toolchain':'fixture', 'repos':packages}
        audit={'toolchain':'fixture', 'packages':{r['package']:{'rev':r['rev']} for r in packages}}
        return state,audit

    def test_shared_names_stay_visible(self):
        state,audit=self.check_state([package('a','Proofs'),package('b','Proofs')])
        result=module.inventory(state,audit)
        self.assertFalse(result['recorded_coverage_complete'])
        self.assertEqual(result['pending_repositories'],['a','b'])
        self.assertEqual(result['packages'][0]['shared_module_namespaces'],{'Proofs':['b']})

    def test_unique_admitted_roots_and_matching_audits(self):
        state,audit=self.check_state([package('a','A.Proofs',True),package('b','B.Proofs',True)])
        result=module.inventory(state,audit)
        self.assertTrue(result['recorded_coverage_complete'])
        self.assertEqual(result['jointly_admitted'],2)
        audit['packages']['b']['rev']='b'*40
        self.assertFalse(module.inventory(state,audit)['recorded_coverage_complete'])
        audit['packages']['b']['rev']='a'*40
        audit['toolchain']='other'
        self.assertFalse(module.inventory(state,audit)['recorded_coverage_complete'])

    def test_held_unique_library_is_not_complete(self):
        state,audit=self.check_state([package('a','A.Proofs',False)])
        state['repos'][0]['joint_note']='joint proof build fails'
        result=module.inventory(state,audit)
        self.assertFalse(result['recorded_coverage_complete'])
        self.assertEqual(result['packages'][0]['sync_note'],'joint proof build fails')
