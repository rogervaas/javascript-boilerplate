'use strict';

exports.up = function (db, callback) {
    db.createTable('order_product', {
        id: { type: 'int', primaryKey: true, autoIncrement: true },
        order_id: { type: 'int' },
        product_id: { type: 'int' },
        quantity: { type: 'int' },
        reference: { type: 'string' },
        width: { type: 'real' },
        height: { type: 'real' },
        price: { type: 'real' },
        thumbnail: { type: 'string' },
        image: { type: 'string' },
        description: { type: 'string' },
    }, callback);
};

exports.down = function (db, callback) {
    db.dropTable('order_product', callback);
};
