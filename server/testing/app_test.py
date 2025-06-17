import pytest
from app import app, db
from models import Plant

@pytest.fixture(scope="module")
def test_client():
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with app.app_context():
        db.create_all()

        # Create a plant with ID 1
        plant = Plant(
            name="Aloe Vera",
            image="https://example.com/aloe.jpg",
            price=19.99,
            is_in_stock=True
        )
        db.session.add(plant)
        db.session.commit()

        yield app.test_client()

        db.session.remove()
        db.drop_all()

def test_plant_by_id_get_route(test_client):
    response = test_client.get('/plants/1')
    assert response.status_code == 200

def test_plant_by_id_get_route_returns_one_plant(test_client):
    response = test_client.get('/plants/1')
    data = response.get_json()

    assert isinstance(data, dict)
    assert "id" in data
    assert "name" in data

def test_plant_by_id_patch_route_updates_is_in_stock(test_client):
    response = test_client.patch('/plants/1', json={"is_in_stock": False})
    data = response.get_json()

    assert isinstance(data, dict)
    assert data["id"] == 1
    assert data["is_in_stock"] is False

def test_plant_by_id_delete_route_deletes_plant(test_client):
    # Create a new plant to delete
    with app.app_context():
        new_plant = Plant(
            name="Live Oak",
            image="https://example.com/live-oak.jpg",
            price=250.00,
            is_in_stock=True
        )
        db.session.add(new_plant)
        db.session.commit()
        plant_id = new_plant.id

    response = test_client.delete(f'/plants/{plant_id}')
    assert response.status_code == 204 or response.data == b''

    get_response = test_client.get(f'/plants/{plant_id}')
    assert get_response.status_code == 404