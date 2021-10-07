#!/usr/bin/env python3
import time
import sys
import json
import hashlib

import cbor2

import config

def main():
    print("maximum slot:", config.MAX_AFTER)
    commissions = load_commissions(config.CACHE_PATH)

    while any(commission['solved'] != True for commission in commissions):
        for commission in commissions:
            if commission['solved']:
                continue
            print(f"Bruting {commission.get('description', '')}")
            brute_commission(commission, config.BRUTE_SLOT_SIZE)
            update_cache(commissions, config.CACHE_PATH)

def default_encoder(encoder, commission):
    encoded_data = [1, [[0, bytes.fromhex(commission.keyHash)], [4, commission.after], [5, commission.before]]]
    encoder.encode(encoded_data)

def brute_commission(commission, slot_size):
    before = commission.get('before', config.DEFAULT_SLOT)
    after = commission.get('after', 0)

    start = time.time()
    for k in range(slot_size):
        if k % config.VERBOSITY == 0 and k > 0:
            print(f"Finished {k/1000000:.2f}M iterations in {time.time() - start:.2f}s ({(k/1000)/(time.time()-start):.2f}k/s)")
        if after + k < config.MAX_AFTER:
            after += 1
        else:
            before += 1
            commission['before'] = before
            after = 0
            commission['after'] = after
            print("Increased 'before' to", before)

        script = Script(keyHash = commission.get('keyHash', ''), before=before, after=after)
        cbor_sig = cbor2.dumps(script, default=default_encoder, value_sharing=False)
        policyid = hashlib.blake2b(b'\x00'+cbor_sig, digest_size=28).hexdigest()
        for target in commission['targets']:
            score = get_hash_score(policyid, target['target'])
            if score > target['score']:
                target['best_result'] = policyid
                target['before'] = before
                target['after'] = after
                target['score'] = score
                commission['before'] = before
                commission['after'] = after
                print(f"Found new highscore!\nTarget: {target['target']}\nFound: {target['best_result']}\nScore: {score}\nParams: Before = {before} \t After = {after}")
            if score == len(target['target']):
                commission['solved'] = True
                commission['before'] = before
                commission['after'] = before
                return
        commission['before'] = before
        commission['after'] = before
                

def get_hash_score(hash_str, target):
    score = 0
    for idx in range(1+len(target)):
        if target[:idx] == hash_str[:idx]:
            score = idx
        else:
            break
    return score
    
    

def update_cache(commissions, path):
    with open(path, 'w') as f_out:
        json.dump(commissions, f_out, indent=2)
        

def load_commissions(path):
    try:
        with open(path) as f_in:
            commissions = json.load(f_in)
    except FileNotFoundError:
        commissions = [
            {
                'before':123456789,
                'after':0,
                'keyHash':'5ac518d814ec179d01fa9b32edca671c17707a1fc50fd7b3c6a62f97',
                'description':'Sample commission to fulfill',
                'solved':False,
                'targets':[
                    {
                        'target':'000000000000000000',
                        'best_result':'',
                        'score':0,
                        'before':0,
                        'after':0,
                    }
                ]
            }
        ]
        with open(path, 'w') as f_out:
            json.dump(commissions, f_out, indent=2)  # create an empty cache
    except json.decoder.JSONDecodeError:
        print("Could not load json, it might be corrupt or malformed", file=sys.stderr)

    return commissions

class Script:
    def __init__(self, keyHash, before, after):
        self.keyHash = keyHash
        self.before = before
        self.after = after
    def __repr__(self):
        json_repr = {
            'type':'all',
            'scripts':[
                {'type':'sig', 'keyHash':self.keyHash},
                {'type':'after', 'slot':self.after},
                {'type':'before', 'slot':self.before},
            ]
        }
        return json.dumps(json_repr, indent=4)

if __name__ == '__main__':
    main()
