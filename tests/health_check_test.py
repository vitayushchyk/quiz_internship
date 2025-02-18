import threading
import time


def test_health_check(client):
    response = client.get("/health-check/")
    assert response.status_code == 200
    assert response.json() == dict(detail="ok", result="working")


def test_health_check_fail(client):
    response = client.get("/health-check/fail")
    assert response.status_code == 404
    assert response.json() == dict(detail="Not Found")


def test_health_check_invalid_methods(client):
    response = client.post("/health-check/")
    assert response.status_code == 405

    response = client.put("/health-check/")
    assert response.status_code == 405

    response = client.delete("/health-check/")
    assert response.status_code == 405


def test_stress_health_check(client, requests=200):
    errors = []

    def make_request():
        response = client.get("/health-check/")
        if response.status_code != 200:
            errors.append(response.status_code)

    threads = [threading.Thread(target=make_request) for _ in range(requests)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors


def test_health_check_performance(client):
    start_time = time.time()
    response = client.get("/health-check/")
    elapsed_time = time.time() - start_time
    assert response.status_code == 200
    assert elapsed_time < 0.5
