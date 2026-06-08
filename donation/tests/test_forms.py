from donation.forms import PledgeForm


def test_pledge_form_valid():
    form = PledgeForm(data={"quantity": 10, "person_name": "John"})
    assert form.is_valid()


def test_pledge_form_rejects_zero_quantity():
    form = PledgeForm(data={"quantity": 0, "person_name": "John"})
    assert not form.is_valid()
    assert "quantity" in form.errors


def test_pledge_form_requires_name():
    form = PledgeForm(data={"quantity": 10, "person_name": ""})
    assert not form.is_valid()
    assert "person_name" in form.errors
