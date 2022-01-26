if __name__ == '__main__':
    import argparse
    import pytest 
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-all', dest='all', help='run all tests', action='store_true')
    parser.add_argument('-schema', dest='schema', help='only run schema tests', action='store_true')
    parser.add_argument('-others', dest='others', help='only run other tests', action='store_true')
    
    args = parser.parse_args()
    if args.all + args.others + args.schema == 0:
        raise Exception('Please select tests to run.')
    elif args.all + args.others + args.schema > 1:
        raise Exception('More than one mode selected.')
    
    ini_args = ['-c', 'flask_app/tests/pytest.ini']
    if args.all:
        pytest.main(ini_args)
    elif args.others:
        pytest.main(['-m', 'not schema'] + ini_args)
    elif args.schema:
        pytest.main(['-m', 'schema'] + ini_args)
    


