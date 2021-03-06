#!/usr/bin/env python2

import argparse
import os
import random

import docker
import shuffle


params = {
    'base': docker.base_choices,
    'cuda': docker.cuda_choices,
    'cudnn': docker.cudnn_choices,
    'nccl': docker.nccl_choices,
    'numpy': ['1.9', '1.10', '1.11', '1.12'],
    'protobuf': ['2', '3', 'cpp-3'],
    'h5py': [None, '2.5', '2.6', '2.7'],
    'pillow': [None, '3.4', '4.0', '4.1'],
    'theano': [None, '0.8', '0.9'],
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Test script for multi-environment')
    parser.add_argument('--id', type=int, required=True)
    parser.add_argument('--cache')
    parser.add_argument('--http-proxy')
    parser.add_argument('--https-proxy')
    parser.add_argument('--no-cache', action='store_true')
    parser.add_argument('--timeout', default='1h')
    parser.add_argument(
        '--gpu-id', type=int,
        help='GPU ID you want to use mainly in the script.')
    parser.add_argument('--interactive', action='store_true')
    args = parser.parse_args()

    conf = shuffle.make_shuffle_conf(params, args.id)
    conf['requires'] = [
        'setuptools',
        'pip',
        'cython==0.24'
    ] + conf['requires'] + [
        'hacking',
        'nose',
        'mock',
        'coverage',
    ]

    volume = []
    env = {'CUDNN': conf['cudnn']}

    if args.cache:
        volume.append(args.cache)
        env['CUPY_CACHE_DIR'] = os.path.join(args.cache, '.cupy')
        env['CCACHE_DIR'] = os.path.join(args.cache, '.ccache')

    if args.http_proxy:
        conf['http_proxy'] = args.http_proxy
    if args.https_proxy:
        conf['https_proxy'] = args.https_proxy

    if args.interactive:
        docker.run_interactive(
            conf, no_cache=args.no_cache, volume=volume, env=env)
    else:
        if conf['cuda'] != 'none':
            docker.run_with(
                conf, './test.sh', no_cache=args.no_cache, volume=volume,
                env=env, timeout=args.timeout, gpu_id=args.gpu_id)
        else:
            docker.run_with(
                conf, './test_cpu.sh', no_cache=args.no_cache, volume=volume,
                env=env, timeout=args.timeout)
