import json
import base64
import pytest
import sys
import os

# Add the parent directory to the path so we can import the Flask app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from index import app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    """Test that the index route returns the HTML page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Numeric Converter' in response.data
    assert b'Input Value:' in response.data


def test_convert_text_to_all_outputs(client):
    """Test converting from text input to all output types."""
    test_cases = [
        ('one', '1'),
        ('two', '2'),
        ('three', '3'),
        ('four', '4'),
        ('five', '5'),
        ('six', '6'),
        ('seven', '7'),
        ('eight', '8'),
        ('nine', '9'),
        ('ten', '10'),
        ('zero', '0'),
        ('nil', '0')
    ]
    
    for text_input, expected_decimal in test_cases:
        # Test text to decimal
        response = client.post('/convert', 
                             data=json.dumps({
                                 'input': text_input,
                                 'inputType': 'text',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is None
        assert data['result'] == expected_decimal
        
        # Test text to binary
        response = client.post('/convert',
                             data=json.dumps({
                                 'input': text_input,
                                 'inputType': 'text',
                                 'outputType': 'binary'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is None
        assert data['result'] == bin(int(expected_decimal))[2:]
        
        # Test text to octal
        response = client.post('/convert',
                             data=json.dumps({
                                 'input': text_input,
                                 'inputType': 'text',
                                 'outputType': 'octal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is None
        assert data['result'] == oct(int(expected_decimal))[2:]
        
        # Test text to hexadecimal
        response = client.post('/convert',
                             data=json.dumps({
                                 'input': text_input,
                                 'inputType': 'text',
                                 'outputType': 'hexadecimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is None
        assert data['result'] == hex(int(expected_decimal))[2:]
        
        # Test text to base64
        response = client.post('/convert',
                             data=json.dumps({
                                 'input': text_input,
                                 'inputType': 'text',
                                 'outputType': 'base64'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['error'] is None
        # Verify it's valid base64 by decoding it back
        decoded = base64.b64decode(data['result'])
        assert int.from_bytes(decoded, byteorder='big') == int(expected_decimal)


def test_convert_binary_to_all_outputs(client):
    """Test converting from binary input to all output types."""
    test_cases = [
        ('1010', '10'),
        ('1111', '15'),
        ('1000000', '64'),
        ('0', '0'),
        ('1', '1')
    ]
    
    for binary_input, expected_decimal in test_cases:
        for output_type in ['decimal', 'octal', 'hexadecimal', 'text', 'base64']:
            response = client.post('/convert',
                                 data=json.dumps({
                                     'input': binary_input,
                                     'inputType': 'binary',
                                     'outputType': output_type
                                 }),
                                 content_type='application/json')
            data = json.loads(response.data)
            assert data['error'] is None
            
            if output_type == 'decimal':
                assert data['result'] == expected_decimal
            elif output_type == 'octal':
                assert data['result'] == oct(int(expected_decimal))[2:]
            elif output_type == 'hexadecimal':
                assert data['result'] == hex(int(expected_decimal))[2:]
            elif output_type == 'text':
                # Check that it's a valid text representation
                assert data['result'] is not None
            elif output_type == 'base64':
                # Verify it's valid base64
                decoded = base64.b64decode(data['result'])
                assert int.from_bytes(decoded, byteorder='big') == int(expected_decimal)


def test_convert_octal_to_all_outputs(client):
    """Test converting from octal input to all output types."""
    test_cases = [
        ('12', '10'),
        ('17', '15'),
        ('100', '64'),
        ('0', '0'),
        ('1', '1')
    ]
    
    for octal_input, expected_decimal in test_cases:
        for output_type in ['decimal', 'binary', 'hexadecimal', 'text', 'base64']:
            response = client.post('/convert',
                                 data=json.dumps({
                                     'input': octal_input,
                                     'inputType': 'octal',
                                     'outputType': output_type
                                 }),
                                 content_type='application/json')
            data = json.loads(response.data)
            assert data['error'] is None
            
            if output_type == 'decimal':
                assert data['result'] == expected_decimal
            elif output_type == 'binary':
                assert data['result'] == bin(int(expected_decimal))[2:]
            elif output_type == 'hexadecimal':
                assert data['result'] == hex(int(expected_decimal))[2:]
            elif output_type == 'text':
                assert data['result'] is not None
            elif output_type == 'base64':
                decoded = base64.b64decode(data['result'])
                assert int.from_bytes(decoded, byteorder='big') == int(expected_decimal)


def test_convert_decimal_to_all_outputs(client):
    """Test converting from decimal input to all output types."""
    test_cases = ['0', '1', '10', '15', '64', '255', '1024']
    
    for decimal_input in test_cases:
        for output_type in ['binary', 'octal', 'hexadecimal', 'text', 'base64']:
            response = client.post('/convert',
                                 data=json.dumps({
                                     'input': decimal_input,
                                     'inputType': 'decimal',
                                     'outputType': output_type
                                 }),
                                 content_type='application/json')
            data = json.loads(response.data)
            assert data['error'] is None
            
            if output_type == 'binary':
                assert data['result'] == bin(int(decimal_input))[2:]
            elif output_type == 'octal':
                assert data['result'] == oct(int(decimal_input))[2:]
            elif output_type == 'hexadecimal':
                assert data['result'] == hex(int(decimal_input))[2:]
            elif output_type == 'text':
                assert data['result'] is not None
            elif output_type == 'base64':
                decoded = base64.b64decode(data['result'])
                assert int.from_bytes(decoded, byteorder='big') == int(decimal_input)


def test_convert_hexadecimal_to_all_outputs(client):
    """Test converting from hexadecimal input to all output types."""
    test_cases = [
        ('a', '10'),
        ('f', '15'),
        ('40', '64'),
        ('0', '0'),
        ('1', '1'),
        ('ff', '255'),
        ('400', '1024')
    ]
    
    for hex_input, expected_decimal in test_cases:
        for output_type in ['decimal', 'binary', 'octal', 'text', 'base64']:
            response = client.post('/convert',
                                 data=json.dumps({
                                     'input': hex_input,
                                     'inputType': 'hexadecimal',
                                     'outputType': output_type
                                 }),
                                 content_type='application/json')
            data = json.loads(response.data)
            assert data['error'] is None
            
            if output_type == 'decimal':
                assert data['result'] == expected_decimal
            elif output_type == 'binary':
                assert data['result'] == bin(int(expected_decimal))[2:]
            elif output_type == 'octal':
                assert data['result'] == oct(int(expected_decimal))[2:]
            elif output_type == 'text':
                assert data['result'] is not None
            elif output_type == 'base64':
                decoded = base64.b64decode(data['result'])
                assert int.from_bytes(decoded, byteorder='big') == int(expected_decimal)


def test_convert_base64_to_all_outputs(client):
    """Test converting from base64 input to all output types."""
    # Create some test base64 values
    test_values = [0, 1, 10, 15, 64, 255, 1024]
    
    for value in test_values:
        # Create base64 representation
        byte_count = (value.bit_length() + 7) // 8
        if value == 0:
            byte_count = 1
        number_bytes = value.to_bytes(byte_count, byteorder='big')
        b64_input = base64.b64encode(number_bytes).decode('utf-8')
        
        for output_type in ['decimal', 'binary', 'octal', 'hexadecimal', 'text']:
            response = client.post('/convert',
                                 data=json.dumps({
                                     'input': b64_input,
                                     'inputType': 'base64',
                                     'outputType': output_type
                                 }),
                                 content_type='application/json')
            data = json.loads(response.data)
            assert data['error'] is None
            
            if output_type == 'decimal':
                assert data['result'] == str(value)
            elif output_type == 'binary':
                assert data['result'] == bin(value)[2:]
            elif output_type == 'octal':
                assert data['result'] == oct(value)[2:]
            elif output_type == 'hexadecimal':
                assert data['result'] == hex(value)[2:]
            elif output_type == 'text':
                assert data['result'] is not None


def test_error_handling_invalid_text_input(client):
    """Test error handling for invalid text inputs."""
    invalid_texts = ['eleven', 'twenty', 'hundred', 'abc', '123', '']
    
    for invalid_text in invalid_texts:
        response = client.post('/convert',
                             data=json.dumps({
                                 'input': invalid_text,
                                 'inputType': 'text',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] is not None
        assert 'Unable to convert text to number' in data['error']


def test_error_handling_invalid_binary_input(client):
    """Test error handling for invalid binary inputs."""
    invalid_binaries = ['2', '3', 'abc', '10102', '']
    
    for invalid_binary in invalid_binaries:
        response = client.post('/convert',
                             data=json.dumps({
                                 'input': invalid_binary,
                                 'inputType': 'binary',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] is not None


def test_error_handling_invalid_octal_input(client):
    """Test error handling for invalid octal inputs."""
    invalid_octals = ['8', '9', 'abc', '128', '']
    
    for invalid_octal in invalid_octals:
        response = client.post('/convert',
                             data=json.dumps({
                                 'input': invalid_octal,
                                 'inputType': 'octal',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] is not None


def test_error_handling_invalid_decimal_input(client):
    """Test error handling for invalid decimal inputs."""
    invalid_decimals = ['3.14', 'abc', '12.5', '']
    
    for invalid_decimal in invalid_decimals:
        response = client.post('/convert',
                             data=json.dumps({
                                 'input': invalid_decimal,
                                 'inputType': 'decimal',
                                 'outputType': 'binary'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] is not None


def test_error_handling_invalid_hexadecimal_input(client):
    """Test error handling for invalid hexadecimal inputs."""
    invalid_hexes = ['g', 'h', 'xyz', '12g', '']
    
    for invalid_hex in invalid_hexes:
        response = client.post('/convert',
                             data=json.dumps({
                                 'input': invalid_hex,
                                 'inputType': 'hexadecimal',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] is not None


def test_error_handling_invalid_base64_input(client):
    """Test error handling for invalid base64 inputs."""
    invalid_base64s = ['%%%', 'abc!', '123@', '']
    
    for invalid_b64 in invalid_base64s:
        response = client.post('/convert',
                             data=json.dumps({
                                 'input': invalid_b64,
                                 'inputType': 'base64',
                                 'outputType': 'decimal'
                             }),
                             content_type='application/json')
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] is not None
        assert 'Invalid base64 input' in data['error']


def test_error_handling_invalid_input_type(client):
    """Test error handling for invalid input types."""
    response = client.post('/convert',
                         data=json.dumps({
                             'input': '10',
                             'inputType': 'invalid_type',
                             'outputType': 'decimal'
                         }),
                         content_type='application/json')
    data = json.loads(response.data)
    assert data['result'] is None
    assert data['error'] is not None
    assert 'Invalid input type' in data['error']


def test_error_handling_invalid_output_type(client):
    """Test error handling for invalid output types."""
    response = client.post('/convert',
                         data=json.dumps({
                             'input': '10',
                             'inputType': 'decimal',
                             'outputType': 'invalid_type'
                         }),
                         content_type='application/json')
    data = json.loads(response.data)
    assert data['result'] is None
    assert data['error'] is not None
    assert 'Invalid output type' in data['error']


def test_error_handling_missing_json_fields(client):
    """Test error handling for missing JSON fields."""
    # Missing input field
    response = client.post('/convert',
                         data=json.dumps({
                             'inputType': 'decimal',
                             'outputType': 'binary'
                         }),
                         content_type='application/json')
    data = json.loads(response.data)
    assert data['result'] is None
    assert data['error'] is not None
    
    # Missing inputType field
    response = client.post('/convert',
                         data=json.dumps({
                             'input': '10',
                             'outputType': 'binary'
                         }),
                         content_type='application/json')
    data = json.loads(response.data)
    assert data['result'] is None
    assert data['error'] is not None
    
    # Missing outputType field
    response = client.post('/convert',
                         data=json.dumps({
                             'input': '10',
                             'inputType': 'decimal'
                         }),
                         content_type='application/json')
    data = json.loads(response.data)
    assert data['result'] is None
    assert data['error'] is not None


def test_roundtrip_conversions(client):
    """Test that conversions work both ways (roundtrip)."""
    # Test decimal -> binary -> decimal
    response = client.post('/convert',
                         data=json.dumps({
                             'input': '42',
                             'inputType': 'decimal',
                             'outputType': 'binary'
                         }),
                         content_type='application/json')
    data = json.loads(response.data)
    binary_result = data['result']
    
    response = client.post('/convert',
                         data=json.dumps({
                             'input': binary_result,
                             'inputType': 'binary',
                             'outputType': 'decimal'
                         }),
                         content_type='application/json')
    data = json.loads(response.data)
    assert data['result'] == '42'
    
    # Test decimal -> hex -> decimal
    response = client.post('/convert',
                         data=json.dumps({
                             'input': '255',
                             'inputType': 'decimal',
                             'outputType': 'hexadecimal'
                         }),
                         content_type='application/json')
    data = json.loads(response.data)
    hex_result = data['result']
    
    response = client.post('/convert',
                         data=json.dumps({
                             'input': hex_result,
                             'inputType': 'hexadecimal',
                             'outputType': 'decimal'
                         }),
                         content_type='application/json')
    data = json.loads(response.data)
    assert data['result'] == '255'


if __name__ == '__main__':
    pytest.main([__file__])
