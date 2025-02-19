def test_create_new_company_success(client, auth_headers):
    response = client.post(
        "/company/",
        json={
            "name": "New Company",
            "description": "Test Description",
            "status": "visible",
            "owner_id": 1,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201, f"Error: {response.text}"
    result = response.json()

    assert result["name"] == "New Company"
    assert result["description"] == "Test Description"
    assert result["owner_id"] == 1


def test_company_already_exist(client, auth_headers):
    response = client.post(
        "/company/",
        json={
            "name": "New Company",
            "description": "Test Description",
            "status": "visible",
            "owner_id": 1,
        },
        headers=auth_headers,
    )
    assert response.status_code == 409, f"Error: {response.text}"


def test_create_new_company_fail_not_unauthorised(client):
    response = client.post(
        "/company/",
        json={
            "name": "New Company",
            "description": "Test Description",
            "status": "visible",
            "owner_id": 1,
        },
    )
    assert response.status_code == 401, f"Error: {response.text}"


def test_get_all_companies(client, auth_headers):
    response = client.get("/company/", headers=auth_headers)
    assert response.status_code == 200, f"Error: {response.text}"
    companies = response.json()
    assert len(companies) >= 1


def test_get_company_by_id(client, auth_headers, existing_company):
    company_id = existing_company["id"]
    response = client.get(f"/company/{company_id}", headers=auth_headers)
    assert response.status_code == 200, f"Error: {response.text}"
    result = response.json()
    assert result["name"] == "New Company"
    assert result["description"] == "Test Description"
    assert result["status"] == "visible"
    assert result["owner_id"] == 1


def test_change_visibility_suc(client, auth_headers, existing_company):
    company_id = existing_company["id"]
    response = client.post(
        f"/company/change-visibility/{company_id}/",
        json={
            "status": "hidden",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200, f"Error: {response.text}"
    result = response.json()
    assert result["name"] == "New Company"
    assert result["description"] == "Test Description"
    assert result["status"] == "hidden"
    assert result["owner_id"] == 1


def test_change_visibility_fail_not_unauthorised(client):
    response = client.post(
        "/company/change-visibility/1/",
        json={
            "status": "hidden",
        },
    )
    assert response.status_code == 401, f"Error: {response.text}"


def test_change_visibility_fail_not_owner(client, not_owner_auth_headers):
    response = client.post(
        "/company/change-visibility/1/",
        json={
            "status": "hidden",
        },
        headers=not_owner_auth_headers,
    )
    assert response.status_code == 403, f"Error: {response.text}"
    assert response.json()["detail"] == f"Unauthorized access to company with ID 1."


def test_change_visibility_fail_not_exist(client, auth_headers):
    response = client.post(
        "/company/change-visibility/100/",
        json={
            "status": "hidden",
        },
        headers=auth_headers,
    )
    assert response.status_code == 404, f"Error: {response.text}"
    assert response.json()["detail"] == "Company with ID 100 not found."


def test_change_visibility_not_rith_status(client, auth_headers, existing_company):
    company_id = existing_company["id"]
    response = client.post(
        f"/company/change-visibility/{company_id}/",
        json={
            "status": "not_rith_status",
        },
        headers=auth_headers,
    )
    assert response.status_code == 400, f"Error: {response.text}"


def test_update_company_manual(client, auth_headers):
    company_id = 1
    response = client.put(
        f"/company/{company_id}",
        json={
            "name": "Another Name",
            "description": "Another Description",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200, f"Error: {response.text}"
    result = response.json()
    assert result["name"] == "Another Name"
    assert result["description"] == "Another Description"


def test_update_company_not_owner(client, not_owner_auth_headers, existing_company):
    company_id = existing_company["id"]
    response = client.put(
        f"/company/{company_id}",
        json={
            "name": "Updated Name",
            "description": "Updated Description",
        },
        headers=not_owner_auth_headers,
    )
    assert (
        response.status_code == 403
    ), f"Expected 403 Forbidden, got {response.status_code}"
    assert (
        response.json()["detail"]
        == f"Unauthorized access to company with ID {company_id}."
    )


def test_update_company(client, auth_headers, existing_company):
    company_id = existing_company["id"]
    response = client.put(
        f"/company/{company_id}",
        json={
            "name": "Updated Name",
            "description": "Updated Description",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200, f"Error: {response.text}"
    result = response.json()
    assert result["name"] == "Updated Name"
    assert result["description"] == "Updated Description"


def test_delete_company_not_owner(client, not_owner_auth_headers, existing_company):
    company_id = existing_company["id"]
    response = client.delete(f"/company/{company_id}", headers=not_owner_auth_headers)
    assert (
        response.status_code == 403
    ), f"Expected 403 Forbidden, got {response.status_code}"
    assert (
        response.json()["detail"]
        == f"Unauthorized access to company with ID {company_id}."
    )


def test_delete_company(client, auth_headers, existing_company):
    company_id = existing_company["id"]
    response = client.delete(f"/company/{company_id}", headers=auth_headers)
    assert response.status_code == 204
