import kfp
from kfp import dsl

def hello_world_op():
    return dsl.ContainerOp(
        name='Hello World',
        image='python:3.9',
        command=['python', '-c'],
        arguments=['print("Hello from Kubeflow!")']
    )

@dsl.pipeline(name='test-pipeline', description='Simple test')
def simple_pipeline():
    hello_world_op()

kfp.compiler.Compiler().compile(simple_pipeline, 'test.yaml')
print("✅ Compiled test.yaml")
