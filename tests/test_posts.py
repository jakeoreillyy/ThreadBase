import pytest
from app import schemas


def test_get_all_posts(client, test_posts):
    response = client.get("/posts/")

    def validate(post):
        return schemas.PostOut(**post)

    post_map = map(validate, response.json())
    post_list = list(post_map)

    assert response.status_code == 200
    assert len(post_list) == len(test_posts)
    assert {p.Post.id for p in post_list} == {p.id for p in test_posts}


def test_incorrect_post_id(client, test_posts):
    response = client.get("/posts/10000")

    assert response.status_code == 404


def test_get_one_post(client, test_posts):
    response = client.get(f"/posts/{test_posts[0].id}")
    post = schemas.PostOut(**response.json())

    assert post.Post.id == test_posts[0].id
    assert post.Post.content == test_posts[0].content
    assert post.Post.title == test_posts[0].title


@pytest.mark.parametrize(
    "title, content, published",
    [
        (
            "Manchester United's Summer Transfer Targets",
            "Elliot Anderson, Lewis Hall, Yann Diomande",
            True,
        ),
        ("Harry Potter Book Series Review", "Really f*cking good", False),
        ("Travel Guide", "Italy - Dolomites", True),
    ],
)
def test_create_post(
    authorized_client, test_user, test_posts, title, content, published
):
    response = authorized_client.post(
        "/posts/", json={"title": title, "content": content, "published": published}
    )

    created_post = schemas.PostResponse(**response.json())

    assert response.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_user["id"]


def test_create_post_default_published(authorized_client, test_user, test_posts):
    response = authorized_client.post(
        "/posts/", json={"title": "title", "content": "content"}
    )

    created_post = schemas.PostResponse(**response.json())

    assert response.status_code == 201
    assert created_post.title == "title"
    assert created_post.content == "content"
    assert created_post.published
    assert created_post.owner_id == test_user["id"]


def test_unauthorized_user_create_post(client, test_user, test_posts):
    response = client.post("/posts/", json={"title": "title", "content": "content"})

    assert response.status_code == 401


def test_unauthorized_user_delete_post(client, test_user, test_posts):
    response = client.delete(f"/posts/{test_posts[0].id}")

    assert response.status_code == 401


def test_successfully_deleted_post(authorized_client, test_user, test_posts):
    response = authorized_client.delete(f"/posts/{test_posts[0].id}")

    assert response.status_code == 204


def test_deleting_non_existent_post(authorized_client, test_user, test_posts):
    response = authorized_client.delete("/posts/10000")

    assert response.status_code == 404


def test_delete_other_users_post(authorized_client, test_user, test_posts):
    other_users_post = next(p for p in test_posts if p.owner_id != test_user["id"])
    response = authorized_client.delete(f"/posts/{other_users_post.id}")

    assert response.status_code == 403


def test_update_post(authorized_client, test_user, test_posts):
    data = {
        "title": "Updated title",
        "content": "Updated content",
        "owner_id": test_posts[0].id,
    }

    response = authorized_client.put(f"/posts/{test_posts[0].id}", json=data)
    updated_post = schemas.PostResponse(**response.json())

    assert response.status_code == 200
    assert updated_post.title == data["title"]
    assert updated_post.content == data["content"]


def test_update_other_users_post(authorized_client, test_user, test_posts):
    other_users_post = next(p for p in test_posts if p.owner_id != test_user["id"])
    data = {
        "title": "Updated title",
        "content": "Updated content",
        "owner_id": other_users_post.id,
    }

    response = authorized_client.put(f"/posts/{other_users_post.id}", json=data)

    assert response.status_code == 403


def test_unauthorized_user_update_post(client, test_user, test_posts):
    response = client.put(f"/posts/{test_posts[0].id}")

    assert response.status_code == 401


def test_updating_non_existent_post(authorized_client, test_user, test_posts):
    data = {
        "title": "Updated title",
        "content": "Updated content",
        "owner_id": test_posts[0].id,
    }
    response = authorized_client.put("/posts/10000", json=data)

    assert response.status_code == 404
