from app import db
from sqlalchemy import text

# initializes db stored functions and adds some values
def initialize_db():
    db.drop_all()
    db.create_all()
    sql = """
    create or replace function add_comparison_item (table_comparison_id int, table_position int) returns void
    as $$
      begin
    
          update comparison_item set position = position + 1 where comparison_id = table_comparison_id and position >= table_position;
          insert into comparison_item (position, comparison_id) values (table_position, table_comparison_id);
          update comparison set last_position = last_position + 1 where id = table_comparison_id;
      end;
    $$ language plpgsql;
    
    create or replace function add_comparison_item_back (table_comparison_id int) returns void
        as $$
        begin
            with temp as (update comparison set last_position = last_position + 1 where id = table_comparison_id returning last_position)
                insert into comparison_item (position, comparison_id) values ((select last_position from temp), table_comparison_id);
        end;
    $$ language plpgsql;
    
    create or replace function delete_comparison_item (table_comparison_id int, table_position int) returns void
        as $$
        begin
            update comparison set last_position = last_position - 1 where id = table_comparison_id;
            delete from comparison_item where comparison_id = table_comparison_id and position = table_position;
            update comparison_item set position = position - 1 where comparison_id = table_comparison_id and position > table_position;
        end;
    $$ language plpgsql;
    
    --TODO: convert so it returns a table
    create or replace function create_comparison_table_stacked (table_comparison_id int) returns void
        as $$
        begin
            drop view if exists comparison_table_stacked;
            create temp view comparison_table_stacked as
                select comparison_attribute.id, comparison_item.position, comparison_attribute.name, attribute_value.val
            from comparison
                inner join comparison_attribute on comparison.id = comparison_attribute.comparison_id
                inner join comparison_item on comparison.id = comparison_item.comparison_id
                left join attribute_value on comparison_item.id = attribute_value.item_id and comparison_attribute.id = attribute_value.attribute_id
                order by position, attribute_id;
        end;
    $$ language plpgsql;
    
    
    create or replace function add_attribute (table_comparison_id int, attribute_name varchar(255), attribute_type_id smallint) returns void
        as $$
        begin
            insert into comparison_attribute (name, type_id, comparison_id) values (attribute_name, attribute_type_id, table_comparison_id);
        end;
    $$ language plpgsql;
    
    create or replace function set_attribute_value (comparison_item_id int, item_attribute_id int, new_value varchar(255)) returns void
        as $$
        begin
            insert into attribute_value (item_id, attribute_id, val) values (comparison_item_id, item_attribute_id, new_value)
                on conflict (item_id, attribute_id) do update
                    set val = new_value;
        end;
    $$ language plpgsql;
    
    create or replace function register_user (_email varchar, _username varchar, _password varchar) returns void
        as $$
        begin
            -- TODO: change it so that password is hashed with salt
            insert into account(email, username, password) values(_email, _username, _password);
        end;
    $$ language plpgsql;
    
    create or replace function get_user_comparisons (_account_id int) returns table(_id int, _name varchar)
        as $$
        begin
            return query select id, name from comparison where account_id = _account_id;
        end;
    $$ language plpgsql;
    
    create or replace function save_comparison_as_template (_comparison_id int, _template_name varchar) returns void
        as $$
            declare _user_template_id int;
        begin
            insert into user_template (name, account_id) select _template_name, account_id from comparison where id = _comparison_id returning id into _user_template_id;
            insert into user_template_attribute (name, type_id, user_template_id, weight) select name, type_id, _user_template_id, weight from comparison_attribute where comparison_id = _comparison_id;
        end;
    $$ language plpgsql;
    
    create or replace function create_comparison_from_user_template (_account_id int, _template_id int, _comparison_name varchar) returns void
        as $$
            declare _comparison_id int;
        begin
            insert into comparison (name, account_id) values (_comparison_name, _account_id) returning id into _comparison_id;
            insert into comparison_attribute (name, type_id, comparison_id, weight) select name, type_id, _comparison_id, weight from template_attribute where id = _template_id;
    
        end;
    $$ language plpgsql;
    
    
    
    /*
    Function taken from Erwin Brandstetter's response on http://stackoverflow.com/questions/36804551/execute-a-dynamic-crosstab-query
    Creates view xtab_view containing pivot table result
    */
    CREATE OR REPLACE FUNCTION xtab(_tbl regclass, _row text, _cat text
                                  , _expr text  -- still vulnerable to SQL injection!
                                  , _type regtype) RETURNS text AS
        $func$
        DECLARE
           _cat_list text;
           _col_list text;
        BEGIN
    
        -- generate categories for xtab param and col definition list
        EXECUTE format(
         $$SELECT string_agg(quote_literal(x.cat), '), (')
                , string_agg(quote_ident  (x.cat), %%L)
           FROM  (SELECT DISTINCT %%I::text AS cat FROM %%s ORDER BY 1) x$$
         , ' ' || _type || ', ', _cat, _tbl)
        INTO  _cat_list, _col_list;
    
        -- generate query string
        RETURN format(
          -- DROP VIEW used instead of CREATE OR REPLACE as column names may change between function calls
          'DROP VIEW IF EXISTS xtab_view;
           CREATE TEMP VIEW xtab_view AS SELECT * FROM crosstab(
           $q$
               SELECT %%I, %%I, %%s
               FROM   %%I
               order by 1, 2
           $q$
         , $c$VALUES (%%5$s)$c$
           ) ct(%%1$I text, %%6$s %%7$s)'
        , _row, _cat, _expr  -- expr must be an aggregate expression!
        , _tbl, _cat_list, _col_list, _type
        );
    
        END
        $func$ LANGUAGE plpgsql;
    
    /*
        Adapted from xtab function above, specifically for creating comparison table view, comparison_table_horizontal, for specified table_comparison_id
    */
    CREATE OR REPLACE FUNCTION create_comparison_table_horizontal(table_comparison_id int) RETURNS text AS
        $func$
        DECLARE
           _cat_list text;
           _col_list text;
        BEGIN
        execute create_comparison_table_stacked(table_comparison_id);
    
        -- generate categories for xtab param and col definition list
        EXECUTE format(
         $$SELECT string_agg(quote_literal(x.cat), '), (')
                , string_agg(quote_ident  (x.cat), %%L)
           FROM  (SELECT generate_series::text AS cat FROM generate_series(0, (SELECT last_position FROM Comparison where id = 1))) x$$
         , ' ' || 'varchar(255)' || ', ')
        INTO  _cat_list, _col_list;
    
        -- generate query string
        RETURN format(
          -- DROP VIEW used instead of CREATE OR REPLACE as column names may change between function calls
          'DROP VIEW IF EXISTS comparison_table_horizontal;
           CREATE TEMP VIEW comparison_table_horizontal AS SELECT * FROM crosstab(
           $q$
               SELECT id, name, position, val
               FROM   comparison_table_stacked
               order by id
           $q$
         , $c$VALUES (%%1$s)$c$
           ) ct(id int, name text, %%2$s varchar(255))'
        , _cat_list, _col_list
        );
    
        END
        $func$ LANGUAGE plpgsql;
    
    -- Sorts specified comparison by specified attribute (ascending)
    -- NOTE: dynamic sql used as you cannot use order by case with casting to different types as column types cannot differ
    -- TODO: try to make more efficient (maybe use sequence instead of row number, combine with dynamic sql portion?)
    -- TODO: consider separating sort update into helper function to take in any list of attribute ids
    -- TODO: look into whether joins would be more efficient (check explain statements)
    create or replace function sort_by_attribute(_comparison_id int, _attribute_id int) returns void as
    $$
    declare _type_id smallint;
    declare _type varchar;
    begin
        select type_id from comparison_attribute where id = _attribute_id into _type_id;
    
        select name from data_type where id = _type_id into _type;
    
        execute format('create or replace temp view sort_view as select comparison_item.id as _item_id from comparison_attribute
            inner join comparison_item on comparison_attribute.comparison_id = comparison_item.comparison_id
            left join attribute_value on attribute_value.item_id = comparison_item.id and attribute_value.attribute_id = comparison_attribute.id
            where comparison_attribute.comparison_id = %%s and comparison_attribute.id = %%s
            order by val::%%s', _comparison_id, _attribute_id, _type);
    
        update comparison_item set position = row_number - 1
        from (select row_number() over (), * from sort_view) as t
        where comparison_id = _comparison_id and comparison_item.id = _item_id;
    
    end;
    $$ language plpgsql;
    
    
    create or replace function populate_database() returns void as
    $$
        begin
            insert into data_type (id, name) values (0, 'vachar'), (1, 'decimal'), (2, 'timestampz');
        end;
    $$ language plpgsql;

    select populate_database()

    """
    db.engine.execute(sql)

if __name__ == 'main':
    initialize_db()