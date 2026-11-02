from app.services.interaction_controller import State,InteractionController


def test_full_flow_and_reentry():
    fsm=InteractionController()
    assert fsm.dispatch('2')==('show_confirmation',)
    assert fsm.state==State.CONFIRMATION and fsm.selected==2
    assert fsm.dispatch('THUMBS_UP')==('show_detail','play_audio')
    assert fsm.state==State.DETAIL and fsm.selected==2
    assert fsm.dispatch('3')==()
    assert fsm.dispatch('THUMBS_UP')==()
    assert fsm.dispatch('FIST')==('stop_audio','show_home')
    assert fsm.selected is None and fsm.state==State.HOME
    assert fsm.dispatch('2')==('show_confirmation',)
    assert fsm.dispatch('THUMBS_UP')==('show_detail','play_audio')

def test_cancel_and_rechoose():
    f=InteractionController()
    assert f.dispatch('7')==('show_confirmation',)
    assert f.dispatch('4')==('show_confirmation',)
    assert f.selected==4
    assert f.dispatch('FIST')==('show_home',)
    assert f.dispatch('THUMBS_UP')==()
    assert f.dispatch('FIST')==()

def test_only_numbers_home():
    f=InteractionController()
    for value in ('UNKNOWN','THUMBS_UP','FIST','11','0'):
        assert f.dispatch(value)==()
        assert f.state==State.HOME
