from donation.forms import PledgeForm


def test_pledge_form_valid():
    form = PledgeForm(data={"quantity": 10})
    assert form.is_valid()


def test_pledge_form_rejects_zero_quantity():
    form = PledgeForm(data={"quantity": 0})
    assert not form.is_valid()
    assert "quantity" in form.errors
