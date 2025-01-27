"""
Containse the functions for building the tables in the SQLite database model.
"""
import sqlite3

class TablesMixin:

    def build_tables(self):
        """
        Creates the following tables for the SQLite database model: 

        - nodes
        - bars
        - sections
        - materials
        - supports
        - loads
        - node reactions
        - node displacements

        Parameters:
        None

        Returns:
        None
        """

        #Build object tables
        self.build_bar_table()
        self.build_node_table()
        self.build_support_table()

        #Build property tables
        self.build_material_table()
        self.build_section_table()

        #Build load tables
        self.build_point_load_table()

        #Build results tables
        self.build_node_displacements_table()
        self.build_node_reactions_table()
    
    def clear_all_tables():

        pass

    def build_bar_table(self):
        """
        Builds the bar table for the model database.

        Parameters:
        connection (SQL connection): Connection to the model database.

        Returns:
        None
        """
        # create a database cursor
        cur = self.connection.cursor()

        # create the database table if it doesn't exist
        bar_table_schema = """
        CREATE TABLE IF NOT EXISTS element_bar (
            _id TEXT PRIMARY KEY,
            node_a INTEGER NOT NULL,
            node_b INTEGER NOT NULL,
            section TEXT NOT NULL,
            orientation_vector TEXT NOT NULL,
            release_a TEXT NOT NULL,
            release_b TEXT NOT NULL,
            PRIMARY KEY(node_a, node_b)
        );
        """
        cur.execute(bar_table_schema)

        cur.close()

    def build_node_table(self):
        """
        Builds the node table for the model database.

        Parameters:
        connection (SQL connection): Connection to the model database.

        Returns:
        None
        """
        # create a database cursor
        cur = self.connection.cursor()

        # create the database table if it doesn't exist
        node_table_schema = """
            CREATE TABLE IF NOT EXISTS element_node (
                _id INTEGER NOT NULL,
                x FLOAT NOT NULL,
                y FLOAT NOT NULL,
                z FLOAT NOT NULL,
                PRIMARY KEY(x, y, z)
            );
            """
        cur.execute(node_table_schema)

        cur.close()

    def build_support_table(self):
        """
        Builds the support table for the model database.

        Parameters:
        connection (SQL connection): Connection to the model database.

        Returns:
        None
        """
        # create a database cursor
        cur = self.connection.cursor()

        # create the database table if it doesn't exist
        support_table_schema = """
            CREATE TABLE IF NOT EXISTS element_support (
                node_index INTEGER NOT NULL PRIMARY KEY,
                fx INTEGER NOT NULL,
                fy INTEGER NOT NULL,
                fz INTEGER NOT NULL,
                mx INTEGER NOT NULL,
                my INTEGER NOT NULL,
                mz INTEGER NOT NULL
            );
            """
        cur.execute(support_table_schema)

        cur.close()

    def build_point_load_table(self):
        """
        Builds the point load table for the model database.

        Parameters:
        connection (SQL connection): Connection to the model database.

        Returns:
        None
        """
        # create a database cursor
        cur = self.connection.cursor()

        # create the database table if it doesn't exist
        point_load_table_schema = """
            CREATE TABLE IF NOT EXISTS load_pointload (
                node_index INTEGER NOT NULL PRIMARY KEY,
                fx FLOAT NOT NULL,
                fy FLOAT NOT NULL,
                fz FLOAT NOT NULL,
                mx FLOAT NOT NULL,
                my FLOAT NOT NULL,
                mz FLOAT NOT NULL
            );
            """
        cur.execute(point_load_table_schema)

        cur.close()

    def build_section_table(self):
        """
        Builds the section table for the model database.

        Parameters:
        connection (SQL connection): Connection to the model database.

        Returns:
        None
        """
        # create a database cursor
        cur = self.connection.cursor()

        # create the database table if it doesn't exist
        section_table_schema = """
            CREATE TABLE IF NOT EXISTS property_section (
                _id TEXT PRIMARY KEY,
                material TEXT NOT NULL,
                area FLOAT NOT NULL,
                izz FLOAT NOT NULL,
                iyy FLOAT NOT NULL
            );
            """
        cur.execute(section_table_schema)

        cur.close()

    def build_material_table(self):
        """
        Builds the material table for the model database.

        Parameters:
        connection (SQL connection): Connection to the model database.

        Returns:
        None
        """
        # create a database cursor
        cur = self.connection.cursor()

        # create the database table if it doesn't exist
        material_table_schema = """
            CREATE TABLE IF NOT EXISTS property_material (
                _id TEXT PRIMARY KEY,
                youngs_modulus FLOAT NOT NULL,
                poissons_ratio FLOAT NOT NULL,
                shear_modulus FLOAT NOT NULL,
                coeff_thermal_expansion FLOAT NOT NULL,
                damping_ratio FLOAT NOT NULL,
                density FLOAT NOT NULL,
                type TEXT,
                region TEXT,
                embodied_carbon FLOAT
            );
            """
        cur.execute(material_table_schema)

        cur.close()

    def build_node_displacements_table(self):
        """
        Builds the node displacements table for the model database.

        Parameters:
        connection (SQL connection): Connection to the model database.

        Returns:
        None
        """
        # create a database cursor
        cur = self.connection.cursor()

        # create the database table if it doesn't exist
        results_node_displacements = """
            CREATE TABLE IF NOT EXISTS result_node_displacement (
            node_index int NOT NULL,
            load_case string NOT NULL,
            ux float NOT NULL,
            uy float NOT NULL,
            uz float NOT NULL,
            rx float NOT NULL,
            ry float NOT NULL,
            rz float NOT NULL
            ); """

        cur.execute(results_node_displacements)

        cur.close()

    def build_node_reactions_table(self):
        """
        Builds the node displacements table for the model database.

        Parameters:
        connection (SQL connection): Connection to the model database.

        Returns:
        None
        """
        # create a database cursor
        cur = self.connection.cursor()

        # create the database table if it doesn't exist
        results_node_reactions = """ CREATE TABLE IF NOT EXISTS
            result_node_reactions (
            node_index int NOT NULL,
            load_case string NOT NULL,
            fx float NOT NULL,
            fy float NOT NULL,
            fz float NOT NULL,
            mx float NOT NULL,
            my float NOT NULL,
            mz float NOT NULL
            ); """

        cur.execute(results_node_reactions)

        cur.close()
