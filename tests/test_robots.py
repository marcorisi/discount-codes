"""Tests for robots.txt endpoint."""


def test_robots_txt_exists(client):
    """Test that /robots.txt is accessible."""
    response = client.get('/robots.txt')
    assert response.status_code == 200


def test_robots_txt_content(client):
    """Test that /robots.txt disallows all crawlers."""
    response = client.get('/robots.txt')
    assert response.status_code == 200
    
    content = response.data.decode('utf-8')
    assert 'User-agent: *' in content
    assert 'Disallow: /' in content


def test_robots_txt_content_type(client):
    """Test that /robots.txt returns plain text."""
    response = client.get('/robots.txt')
    assert response.content_type == 'text/plain; charset=utf-8'
