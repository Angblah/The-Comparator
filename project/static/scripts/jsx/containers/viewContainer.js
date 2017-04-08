import React from 'react';
import { ActionCreators as UndoActionCreators } from 'redux-undo'
import {connect} from 'react-redux'
import {addItem, addAttr, editAttr, editItem, editItemName, changeView, deleteAttr, deleteItem} from '../actions/actions'
import ChartView from '../components/chartView'
import ZoomDragCircle from '../components/spiderView'
import ProgressChart from '../components/testView'

class ViewContainer extends React.Component {
    render() {
        //TODO: Create ViewContainer toggle based on view of state.
        if (this.props.view === 'CHART') {
            return (
                <div>
                    <ChartView items={this.props.items}
                       attributes={this.props.attributes}
                       id={this.props.id}
                       editAttr={this.props.editAttr}
                       editItem={this.props.editItem}
                       editItemName={this.props.editItemName}
                       deleteAttr={this.props.deleteAttr}
                       deleteItem={this.props.deleteItem}
                       addAttr={this.props.addAttr}
                       addItem={this.props.addItem}/>
                    <span/>
                </div>
            );
        } else {
            return (
                <div>
                    <ZoomDragCircle items={this.props.items}
                       attributes={this.props.attributes}/>
                    <ProgressChart/>
                    <span/>
                </div>
            );
        }
    }
}

const mapStateToProps = (state) => {
    return {
        id: state.id,
        info: state.info,
        attributes: state.data.present.attributes,
        items: state.data.present.items,
        view: state.data.present.view,
        canUndo: state.data.past.length > 0,
        canRedo: state.data.future.length > 0
    };
}

const mapDispatchToProps = (dispatch, ownProps) => {
    return {
        addAttr: (compId) => {
            dispatch(addAttr(compId))
        },
        addItem: (compId) => {
            dispatch(addItem(compId))
        },
        editAttr: (id, name) => {
            dispatch(editAttr(id, name))
        },
        editItem: (itemId, attrId, value) => {
            dispatch(editItem(itemId, attrId, value))
        },
        editItemName: (itemId, value) => {
            dispatch(editItemName(itemId, value))
        },
        changeView: (view) => {
            dispatch(changeView(view))
        },
        deleteItem: (itemId) => {
            dispatch(deleteItem(itemId))
        },
        deleteAttr: (attrId) => {
            dispatch(deleteAttr(attrId))
        },
        onUndo: () => dispatch(UndoActionCreators.undo()),
        onRedo: () => dispatch(UndoActionCreators.redo())
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(ViewContainer)