import readme_module


print('__main__')


if __name__ == '__main__':
    print("if __name__ == '__main__':")
    readme_module.run_multiprocessing()

# Output:
# __main__
# if __name__ == '__main__':
# __main__
# readme_module
#
# Note:
# '__main__' and 'readme_module' will be printed
# '__main__' will be printed twice, because this module is imported in the other process
