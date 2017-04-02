import {combineReducers} from 'redux';
import undoable, {distinctState} from 'redux-undo';
import attributes from './attributes';
import items from './items';
import view from './view';

const data = undoable(combineReducers({
        view: view,
        attributes: attributes,
        items: items
    }), 
    {filter: distinctState()});

export default data;