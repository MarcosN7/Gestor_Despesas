import sqlite3
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import plotly.express as px
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from datetime import datetime
import os

# --- CLASSE DE GESTÃO DA BASE DE DADOS ---

class DatabaseManager:
    def __init__(self, db_name="expenses.db"):
        self.db_name = db_name
        self._conn = None
        self.setup()

    def _get_connection(self):
        """Retorna uma conexão com a base de dados."""
        return sqlite3.connect(self.db_name)

    def _migrate_database(self):
        """Verifica e adiciona novas colunas à tabela se necessário."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(expenses)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'currency' not in columns:
            cursor.execute("ALTER TABLE expenses ADD COLUMN currency TEXT NOT NULL DEFAULT 'EUR'")
            conn.commit()
            print("Coluna 'currency' adicionada à base de dados.")
            
        conn.close()

    def setup(self):
        """Cria a tabela 'expenses' e executa migrações."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        self._migrate_database()

    def add_expense(self, year, month, category, amount, currency):
        """Adiciona uma nova despesa com a sua moeda."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (year, month, category, amount, currency) VALUES (?, ?, ?, ?, ?)",
                       (year, month, category, amount, currency))
        conn.commit()
        conn.close()

    def delete_expense(self, expense_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        conn.close()

    def get_data_as_dataframe(self, filters=None):
        conn = self._get_connection()
        query = "SELECT id, year, month, category, amount, currency FROM expenses"
        conditions, params = [], []

        if filters:
            # --- Alterações aqui ---
            if filters.get("year") not in (None, "Todos os Anos"):
                conditions.append("year = ?"); params.append(filters["year"])
            if filters.get("month") not in (None, "Todos os Meses"):
                conditions.append("month = ?"); params.append(filters["month"])
            if filters.get("category") not in (None, "Todas as Categorias"):
                conditions.append("category = ?"); params.append(filters["category"])
            if filters.get("currency") not in (None, "Todas as Moedas"):
                conditions.append("currency = ?"); params.append(filters["currency"])
            # --- Fim das alterações ---
        
        if conditions: query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY year DESC, month DESC, id DESC"
        
        df = pd.read_sql_query(query, conn, params=tuple(params))
        conn.close()
        return df

# --- CLASSE PRINCIPAL DA APLICAÇÃO ---

class ExpenseTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.db = DatabaseManager()

        self.title("Gestor de Despesas Pessoal v3.0 - Multimoeda")
        self.geometry("1300x700")

        self.currency_map = {"BRL": "R$", "USD": "$", "EUR": "€"}
        self.month_map = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12}
        self.month_map_inv = {v: k for k, v in self.month_map.items()}
        self.categories = ["Alimentação", "Moradia", "Transporte", "Serviços", "Lazer", "Outros"]
        self.years = [str(i) for i in range(datetime.now().year + 1, 2020, -1)]
        self.current_filters = {}

        self.setup_ui()
        self.populate_table()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        self.setup_left_panel()
        self.setup_right_panel()

    def setup_left_panel(self):
        left_frame = ctk.CTkFrame(self, width=280, corner_radius=10); left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew"); left_frame.grid_propagate(False)
        ctk.CTkLabel(left_frame, text="Adicionar Despesa", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, columnspan=2, padx=20, pady=20)
        ctk.CTkLabel(left_frame, text="Moeda:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.currency_optionmenu = ctk.CTkOptionMenu(left_frame, values=list(self.currency_map.keys())); self.currency_optionmenu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(left_frame, text="Ano:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.year_optionmenu = ctk.CTkOptionMenu(left_frame, values=self.years); self.year_optionmenu.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(left_frame, text="Mês:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.month_optionmenu = ctk.CTkOptionMenu(left_frame, values=list(self.month_map.keys())); self.month_optionmenu.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(left_frame, text="Categoria:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.category_optionmenu = ctk.CTkOptionMenu(left_frame, values=self.categories); self.category_optionmenu.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(left_frame, text="Valor:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.amount_entry = ctk.CTkEntry(left_frame, placeholder_text="Ex: 50.75"); self.amount_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
        self.add_button = ctk.CTkButton(left_frame, text="Adicionar Despesa", command=self.add_expense); self.add_button.grid(row=6, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        ttk.Separator(left_frame, orient='horizontal').grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky='ew')
        ctk.CTkLabel(left_frame, text="Ações", font=ctk.CTkFont(size=16, weight="bold")).grid(row=8, column=0, columnspan=2, padx=20, pady=10)
        self.delete_button = ctk.CTkButton(left_frame, text="Apagar Despesa Selecionada", command=self.delete_expense, fg_color="#D32F2F", hover_color="#B71C1C"); self.delete_button.grid(row=9, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        self.export_csv_button = ctk.CTkButton(left_frame, text="Exportar Tudo para CSV", command=self.export_to_csv); self.export_csv_button.grid(row=10, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

    def setup_right_panel(self):
        right_frame = ctk.CTkFrame(self, corner_radius=10); right_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew"); right_frame.grid_columnconfigure(0, weight=1); right_frame.grid_rowconfigure(2, weight=1)
        top_frame = ctk.CTkFrame(right_frame); top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(top_frame, text="Filtrar por:").grid(row=0, column=0, padx=5, pady=5)
        
        # --- Alterações aqui ---
        self.filter_currency_optionmenu = ctk.CTkOptionMenu(top_frame, values=["Todas as Moedas"] + list(self.currency_map.keys()), width=140)
        self.filter_currency_optionmenu.grid(row=0, column=1, padx=5, pady=5)
        
        self.filter_year_optionmenu = ctk.CTkOptionMenu(top_frame, values=["Todos os Anos"] + self.years, width=130)
        self.filter_year_optionmenu.grid(row=0, column=2, padx=5, pady=5)

        self.filter_month_optionmenu = ctk.CTkOptionMenu(top_frame, values=["Todos os Meses"] + list(self.month_map.keys()), width=140)
        self.filter_month_optionmenu.grid(row=0, column=3, padx=5, pady=5)

        self.filter_category_optionmenu = ctk.CTkOptionMenu(top_frame, values=["Todas as Categorias"] + self.categories)
        self.filter_category_optionmenu.grid(row=0, column=4, padx=5, pady=5)
        # --- Fim das alterações ---

        self.filter_button = ctk.CTkButton(top_frame, text="Aplicar", command=self.apply_filters); self.filter_button.grid(row=0, column=5, padx=5, pady=5)
        self.reset_button = ctk.CTkButton(top_frame, text="Limpar", command=self.reset_filters, fg_color="gray"); self.reset_button.grid(row=0, column=6, padx=5, pady=5)
        
        summary_frame = ctk.CTkFrame(right_frame, fg_color="transparent"); summary_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.total_label = ctk.CTkLabel(summary_frame, text="Total na Vista: ", font=ctk.CTkFont(size=14, weight="bold")); self.total_label.pack(side="left", padx=10)
        
        charts_frame = ctk.CTkFrame(right_frame); charts_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(charts_frame, text="Visualizações:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=10)
        self.charts_button = ctk.CTkButton(charts_frame, text="Gráficos Padrão", command=self.generate_graphs); self.charts_button.pack(side="left", padx=5, pady=5)
        self.pdf_button = ctk.CTkButton(charts_frame, text="Exportar Resumo p/ PDF", command=self.export_to_pdf); self.pdf_button.pack(side="left", padx=5, pady=5)
        
        self.setup_table(right_frame)

    def setup_table(self, parent_frame):
        table_frame = ctk.CTkFrame(parent_frame); table_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew"); table_frame.grid_columnconfigure(0, weight=1); table_frame.grid_rowconfigure(0, weight=1)
        style = ttk.Style(); style.theme_use("default"); style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=25, fieldbackground="#343638", bordercolor="#343638", borderwidth=0); style.map('Treeview', background=[('selected', '#22559b')]); style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat", font=('Calibri', 10, 'bold')); style.map("Treeview.Heading", background=[('active', '#3484F0')])
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Ano", "Mês", "Categoria", "Valor"), show="headings")
        self.tree.heading("ID", text="ID"); self.tree.heading("Ano", text="Ano"); self.tree.heading("Mês", text="Mês"); self.tree.heading("Categoria", text="Categoria"); self.tree.heading("Valor", text="Valor")
        self.tree.column("ID", width=40, anchor="center"); self.tree.column("Ano", width=60, anchor="center"); self.tree.column("Mês", width=100, anchor="center"); self.tree.column("Categoria", width=150, anchor="center"); self.tree.column("Valor", width=100, anchor="e")
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ctk.CTkScrollbar(table_frame, command=self.tree.yview); scrollbar.grid(row=0, column=1, sticky="ns"); self.tree.configure(yscrollcommand=scrollbar.set)

    def populate_table(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        df = self.db.get_data_as_dataframe(self.current_filters)
        for _, row in df.iterrows():
            month_name = self.month_map_inv.get(row['month'], "N/A")
            currency_symbol = self.currency_map.get(row['currency'], "")
            formatted_amount = f"{currency_symbol} {row['amount']:.2f}"
            formatted_row = [row['id'], row['year'], month_name, row['category'], formatted_amount]
            self.tree.insert("", "end", values=formatted_row)
        self.update_summary()

    def add_expense(self):
        currency = self.currency_optionmenu.get()
        year = self.year_optionmenu.get()
        month_name = self.month_optionmenu.get(); month_num = self.month_map.get(month_name)
        category = self.category_optionmenu.get()
        amount_str = self.amount_entry.get()
        if not amount_str: messagebox.showerror("Erro", "O campo 'Valor' é obrigatório."); return
        try:
            amount = float(amount_str.replace(',', '.'))
            if amount <= 0: raise ValueError("O valor deve ser positivo.")
        except ValueError as e: messagebox.showerror("Erro", f"Valor inválido: {e}"); return
        self.db.add_expense(int(year), month_num, category, amount, currency)
        messagebox.showinfo("Sucesso", "Despesa adicionada!"); self.amount_entry.delete(0, 'end')
        self.populate_table()

    def delete_expense(self):
        selected_items = self.tree.selection()
        if not selected_items: messagebox.showinfo("Aviso", "Selecione uma despesa para apagar."); return
        if messagebox.askyesno("Confirmar", f"Apagar {len(selected_items)} despesa(s) selecionada(s)?"):
            for item_id in selected_items:
                self.db.delete_expense(self.tree.item(item_id)['values'][0])
            self.populate_table()
            messagebox.showinfo("Sucesso", "Despesas apagadas.")

    def apply_filters(self):
        month_name = self.filter_month_optionmenu.get()
        self.current_filters = {
            "currency": self.filter_currency_optionmenu.get(),
            "year": self.filter_year_optionmenu.get(),
            "month": self.month_map.get(month_name) if month_name != "Todos" else "Todos",
            "category": self.filter_category_optionmenu.get()
        }
        self.populate_table()

    def reset_filters(self):
        # --- Alterações aqui ---
        self.filter_currency_optionmenu.set("Todas as Moedas")
        self.filter_year_optionmenu.set("Todos os Anos")
        self.filter_month_optionmenu.set("Todos os Meses")
        self.filter_category_optionmenu.set("Todas as Categorias")
        # --- Fim das alterações ---
        self.current_filters = {}
        self.populate_table()

    def update_summary(self):
        df = self.db.get_data_as_dataframe(self.current_filters)
        if df.empty:
            self.total_label.configure(text="Total na Vista: N/A")
            return
        
        currencies_in_view = df['currency'].unique()
        if len(currencies_in_view) == 1:
            total = df['amount'].sum()
            symbol = self.currency_map.get(currencies_in_view[0], "")
            self.total_label.configure(text=f"Total na Vista: {symbol} {total:.2f}")
        else:
            self.total_label.configure(text="Total na Vista: Múltiplas Moedas")

    def _pre_export_check(self):
        """Verifica se há dados e se a moeda é única antes de gerar gráficos/PDF."""
        df = self.db.get_data_as_dataframe(self.current_filters)
        if df.empty:
            messagebox.showinfo("Sem Dados", "Não há dados na vista atual para gerar o relatório."); return None
        
        currencies = df['currency'].unique()
        if len(currencies) > 1:
            messagebox.showwarning("Múltiplas Moedas", "Gráficos e relatórios só podem ser gerados para uma única moeda de cada vez.\n\nPor favor, use o filtro 'Moeda' para selecionar apenas uma.")
            return None
        
        return df

    def generate_graphs(self):
        df = self._pre_export_check()
        if df is None: return
        
        symbol = self.currency_map.get(df['currency'].iloc[0], '')
        category_spending = df.groupby('category')['amount'].sum().reset_index()
        fig = px.bar(category_spending, x='category', y='amount', title="Gastos por Categoria", labels={'amount': f'Valor ({symbol})', 'category': 'Categoria'})
        fig.show()

    def export_to_pdf(self):
        df = self._pre_export_check()
        if df is None:
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if not filepath:
            return

        try:
            currency_code = df['currency'].iloc[0]
            symbol = self.currency_map.get(currency_code, "")

            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter

            # --- Primeira Página: Resumo e Gráfico de Barras ---
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(width / 2.0, height - inch, "Relatório de Despesas")

            c.setFont("Helvetica-Oblique", 10)
            filter_text = f"Relatório para a moeda: {currency_code} ({symbol})"
            c.drawCentredString(width / 2.0, height - 1.25 * inch, filter_text)

            total_view = df['amount'].sum()
            c.setFont("Helvetica-Bold", 12)
            c.drawString(inch, height - 2.0 * inch, "Resumo")
            c.setFont("Helvetica", 11)
            c.drawString(inch, height - 2.25 * inch, f"Total Gasto: {symbol} {total_view:.2f}")
            c.drawString(inch, height - 2.50 * inch, f"Número de Transações: {len(df)}")

            c.setFont("Helvetica-Bold", 12)
            c.drawString(inch, height - 3.25 * inch, "Gastos por Categoria")
            
            category_spending = df.groupby('category')['amount'].sum().reset_index()
            fig_bar = px.bar(category_spending, x='category', y='amount', text_auto='.2f')
            fig_bar.update_layout(title_text='', yaxis_title=f"Valor ({symbol})", xaxis_title="")
            
            bar_chart_path = "temp_bar_chart.png"
            fig_bar.write_image(bar_chart_path, width=700, height=400)
            
            c.drawImage(bar_chart_path, inch, height - 7.0 * inch, width=6.5*inch, height=3.5*inch, preserveAspectRatio=True, anchor='n')
            
            os.remove(bar_chart_path)

            # --- Segunda Página: Gráfico Circular ---
            if not df.empty and df['amount'].sum() > 0:
                c.showPage()
                c.setFont("Helvetica-Bold", 18)
                c.drawCentredString(width / 2.0, height - inch, "Distribuição de Despesas")

                fig_pie = px.pie(df, names='category', values='amount')
                fig_pie.update_layout(title_text='')

                pie_chart_path = "temp_pie_chart.png"
                fig_pie.write_image(pie_chart_path, width=600, height=450)

                c.drawImage(pie_chart_path, width/2 - (5*inch)/2, height - 6.5*inch, width=5*inch, height=4.5*inch, preserveAspectRatio=True)

                os.remove(pie_chart_path)

            # --- Terceira Página: Gráfico de Linha (Evolução Mensal) ---
            df_line = df.copy()
            df_line['period'] = pd.to_datetime(df_line['year'].astype(str) + '-' + df_line['month'].astype(str), format='%Y-%m')
            monthly_totals = df_line.groupby(pd.Grouper(key='period', freq='M'))['amount'].sum().reset_index()
            monthly_totals['period'] = monthly_totals['period'].dt.strftime('%Y-%m') # Formata para o gráfico

            # Só cria o gráfico de linha se houver mais de 1 mês com dados
            if len(monthly_totals) > 1:
                c.showPage()
                c.setFont("Helvetica-Bold", 18)
                c.drawCentredString(width / 2.0, height - inch, "Evolução Mensal das Despesas")

                fig_line = px.line(monthly_totals, x='period', y='amount', title="", markers=True, text=monthly_totals['amount'].round(2))
                fig_line.update_traces(textposition="top center")
                fig_line.update_layout(yaxis_title=f'Total Gasto ({symbol})', xaxis_title='Mês')

                line_chart_path = "temp_line_chart.png"
                fig_line.write_image(line_chart_path, width=700, height=400)

                c.drawImage(line_chart_path, inch, height - 6.0 * inch, width=6.5*inch, height=3.5*inch, preserveAspectRatio=True, anchor='n')

                os.remove(line_chart_path)

            c.save()
            messagebox.showinfo("Sucesso", f"PDF exportado com sucesso para {filepath}")

        except Exception as e:
            messagebox.showerror("Erro ao Gerar PDF", f"Ocorreu um erro: {e}")
            print(f"DEBUG: Erro na geração do PDF: {e}")

    def export_to_csv(self):
        df = self.db.get_data_as_dataframe()
        if df.empty: messagebox.showinfo("Sem Dados", "Não há nada para exportar."); return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filepath:
            df['month'] = df['month'].map(self.month_map_inv)
            df.to_csv(filepath, index=False, decimal=',', sep=';')
            messagebox.showinfo("Sucesso", f"Todos os dados foram exportados para {filepath}")


if __name__ == "__main__":
    app = ExpenseTrackerApp()
    app.mainloop()