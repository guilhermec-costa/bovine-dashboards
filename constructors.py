import streamlit as st
from streamlit.delta_generator import DeltaGenerator

class ExpanderConstructor:
    default_container_size = True

    def __init__(self, qtd_of_col : int, type_of_plot: str, content: any, label: str, container_size: bool = default_container_size) -> None:
        self.qtd_of_col = qtd_of_col
        self.expander = st.expander(label)
        self.content = content
        self.type_of_plot = type_of_plot
        self.expander_size = container_size
        self._plot_is_valid = self.__validte_plot
    
    def build_expander(self):
        if self._plot_is_valid:
            with self.expander:
                columns = st.columns(self.qtd_of_col)
                self.__validate_and_build_expander(columns, content=self.content)
        else:
            st.error('Não é um expander válido')

    def __validte_plot(self):
        return True if self.qtd_of_col == len(self.content) else False

    def __validate_and_build_expander(self, columns: DeltaGenerator, content) -> None:
        if self.__check_columns_size(columns) == 'multiple_columns': self.__plot_in_multiple_columns(columns, content, self.expander_size)
        else: self.__plot_in_solo_column(content, container_width=self.expander_size)

    def __check_columns_size(self, columns: DeltaGenerator) -> str:
        return 'multiple_columns' if len(columns) > 1 else None
    
    def __plot_in_multiple_columns(self, columns: DeltaGenerator, content, container_width) -> None:
        for index, col in enumerate(columns):
            if self.type_of_plot == 'plotly_chart': col.plotly_chart(content[index], use_container_width=container_width)
            else: col.write(self.content[index])

    def __plot_in_solo_column(self, content, container_width):
        st.plotly_chart(content, use_container_width=container_width)

    def add_plot(self, number_of_cols: int, content, add_markdown : bool = True, container_size=default_container_size) -> None:
        with self.expander:
            new_cols = st.columns(number_of_cols)
            self.__validate_and_build_expander(new_cols, content=content)

            st.markdown('---') if add_markdown else None