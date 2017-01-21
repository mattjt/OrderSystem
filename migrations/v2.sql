ALTER TABLE ordersystem.orders ADD approved_by INT NOT NULL;
ALTER TABLE ordersystem.orders ADD CONSTRAINT orders_users_id_fk FOREIGN KEY (approved_by) REFERENCES users (id);