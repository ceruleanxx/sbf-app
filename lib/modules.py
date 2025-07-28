import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import streamlit as st
import pandas as pd
from datetime import date



def filter_cond(row):
    availability_date_raw = st.session_state.get('availability_date', date.today())
    availability_date = pd.Timestamp(availability_date_raw)
    return (
        row['Probable Completion Date'] > availability_date or
        row['Standard (Y/N)'] == 'N' or
        row['Chinese'] == 0
    )

def unit_count_by_room_type(df):
    try:
        df_sub = pd.DataFrame(columns=['# 4-rooms Available','# 5-rooms Available','Non-Chinese Quota'])
        
        # Compute count for each room type
        rm_4_count = df[df['Type (4/5-rm)'] == 4].shape[0]
        rm_5_count = df[df['Type (4/5-rm)'] == 5].shape[0]
        nonchinese = df[df['Chinese'] == 0].shape[0]

        # Add a row to the empty DataFrame
        df_sub.loc[0] = [rm_4_count, rm_5_count, nonchinese]
        st.write(df_sub)
    
    except Exception as e:
        st.error(f'[Unit Count by Room Type] : Error occured - {e}')


def highlight_future_rows(row):
    if (filter_cond(row)):
        return ['background-color: #602f6b'] * len(row)  # light yellow
    else:
        return[''] * len(row)
    
def project_summary(df):
    try:
        df['Units Avail'] = df.groupby('Project Name')['Project Name'].transform('count')
        distinct_rows = df[['Project Name', 
                            'Highest Floor', 
                            'Probable Completion Date',
                            'Remaining lease',
                            'Total Units',
                            'Block',
                            'Chinese',
                            'Units Avail',
                            'Standard (Y/N)'
                            ]].drop_duplicates().reset_index(drop=True)

        distinct_rows = distinct_rows.sort_values(by='Probable Completion Date')
        distinct_rows = distinct_rows.style.apply(highlight_future_rows, axis=1)

        st.write(distinct_rows)
    except Exception as e:
        st.error(f'[ProjectSummary] : Error occured - {e}')

    


def pie_chart(df):
    try:
        room_type = st.session_state.get("room_type",4)
        df = df[df['Type (4/5-rm)'] == room_type]
        count_total = df.shape[0]
        count_valid = df[~df.apply(filter_cond, axis=1)].drop_duplicates().shape[0]
        count_invalid = count_total - count_valid

        labels = [f'Total Units {count_total}', f'Ideal Units {count_valid}']
        values = [count_invalid, count_valid]
        colors = ['#602f6b', '#d3c0dc']  # purple and light purple
        
        fig, ax = plt.subplots(figsize=(2, 2))  # Smaller figure size to shrink the chart
        ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            counterclock=False,
            colors=colors,
            textprops={'fontsize': 6}
        )
        ax.set_title(f'% of Interested Units within town', fontsize=6)

        st.pyplot(fig)
    
    except Exception as e:
        st.error(f'[Pie Chart] : Error occured - {e}')



def stack_projs_available(df):  # Stacked side bar chart
    try:
        summary = df.groupby('Project Name').agg(
            units_for_sale=('Project Name', 'count'),
            total_units=('Total Units', 'max')
        ).reset_index()

        summary['remaining_units'] = summary['total_units'] - summary['units_for_sale']
        summary = summary.sort_values('total_units', ascending=True)

        # Dynamic figure height
        fig_height = max(1, 0.6 * len(summary))
        fig, ax = plt.subplots(figsize=(16, fig_height))

        # Draw base bars (grey = remaining)
        bars1 = ax.barh(
            summary['Project Name'], summary['remaining_units'],
            color='lightgrey', label='Remaining Units'
        )

        # Draw overlay bars (purple = available)
        bars2 = ax.barh(
            summary['Project Name'], summary['units_for_sale'],
            left=summary['remaining_units'],
            color='#d3c0dc', label='Units for Sale'
        )

        # Add labels using actual bar positions
        for bar1, bar2, (_, row) in zip(bars1, bars2, summary.iterrows()):
            y_center = bar1.get_y() + bar1.get_height() / 2

            # Total units - centered in full bar
            ax.text(
                row['total_units'] / 2, y_center,
                f"{row['total_units']}",
                ha='center', va='center', color='black', fontsize=8
            )
        
            # Units for sale - at end of purple bar
            if row['units_for_sale'] > 0:
                ax.text(
                    bar2.get_x() + bar2.get_width() - 0.5, y_center,
                    f"{row['units_for_sale']}",
                    ha='right', va='center', color='black', fontsize=8
                )

        ax.set_xlabel("Number of Units")
        ax.set_title("Available Units for Sale by Project", fontsize=13)
        ax.legend(loc='lower right')

        st.pyplot(fig)

    except Exception as e:
        st.error(f'[Stacked Horizontal Bar] : Error occurred - {e}')




def unit_floor_distribution_4rm(df): # FacetGrid 
    try:
        st.write("Each Subplot x-axis represents lowest to top floor, with distribution of 4-room units on offer")
        df = df[df['Type (4/5-rm)'] == 4]
        print('number of 4-room : ' + str(df.shape[0]))
        df = df.sort_values(by='Probable Completion Date')
        project_order = df['Project Name'].unique().tolist()

        # Create FacetGrid of histograms
        g = sns.FacetGrid(df, col="Project Name", col_wrap=4, col_order=project_order, sharex=False, sharey=True)
        g.map(sns.histplot, 'Normalized_Floor', bins=15, kde=True, color='#602f6b')

        # Loop through each subplot to adjust x-axis labels and limits
        for idx, ax in enumerate(g.axes.flatten()):
            project_name = project_order[idx]
            # Get the max floor for that project
            highest_floor = df[df["Project Name"] == project_name]['Highest Floor'].max()
            
            # Set x-axis limits from 0 to 1 (normalized floor range)
            ax.set_xlim(0, 1)

            # Customize ticks: show floors scaled by highest floor
            xticks = ax.get_xticks()
            xticks = [x for x in xticks if 0 <= x <= 1]

            # Map them to actual floor numbers
            new_labels = [int(round(x * highest_floor)) for x in xticks]

            ax.set_xticks(xticks)
            ax.set_xticklabels(new_labels)
            ax.tick_params(axis='x', labelrotation=0)
            ax.set_xlabel('Floor Number', fontsize=9)
            
        # Final layout tweaks
        g.set_axis_labels("Floor Number", "Unit Count")
        g.set_titles(col_template="{col_name}")
        g.fig.subplots_adjust(hspace=0.5, top=0.88, bottom=0.08)

        # Fix for labels being cut off
        g.fig.suptitle('Distribution of 4-rm Flats by Project (Actual Floor)', fontsize=12)
                
        st.pyplot(g.fig)

    except Exception as e:
        st.error(f'[FacetGrid] : Error occured - {e}')



def unit_floor_distribution_5rm(df): # FacetGrid 
    try:
        st.write("Each Subplot x-axis represents lowest to top floor, with distribution of 5-room units on offer")
        df = df[df['Type (4/5-rm)'] == 5]
        print('number of 5-room : ' + str(df.shape[0]))
        df = df.sort_values(by='Probable Completion Date')
        project_order = df['Project Name'].unique().tolist()

        # Create FacetGrid of histograms
        g = sns.FacetGrid(df, col="Project Name", col_wrap=4, col_order=project_order, sharex=False, sharey=True)
        g.map(sns.histplot, 'Normalized_Floor', bins=15, kde=True, color='#602f6b')

        # Loop through each subplot to adjust x-axis labels and limits
        for idx, ax in enumerate(g.axes.flatten()):
            project_name = project_order[idx]
            # Get the max floor for that project
            highest_floor = df[df["Project Name"] == project_name]['Highest Floor'].max()
            
            # Set x-axis limits from 0 to 1 (normalized floor range)
            ax.set_xlim(0, 1)

            # Customize ticks: show floors scaled by highest floor
            xticks = ax.get_xticks()
            xticks = [x for x in xticks if 0 <= x <= 1]

            # Map them to actual floor numbers
            new_labels = [int(round(x * highest_floor)) for x in xticks]

            ax.set_xticks(xticks)
            ax.set_xticklabels(new_labels)
            ax.tick_params(axis='x', labelrotation=0)
            ax.set_xlabel('Floor Number', fontsize=9)
            
        # Final layout tweaks
        g.set_axis_labels("Floor Number", "Unit Count")
        g.set_titles(col_template="{col_name}")
        g.fig.subplots_adjust(hspace=0.5, top=0.88, bottom=0.08)

        # Fix for labels being cut off
        g.fig.suptitle('Distribution of 5-rm Flats by Project (Actual Floor)', fontsize=12)
                
        st.pyplot(g.fig)

    except Exception as e:
        st.error(f'[FacetGrid] : Error occured - {e}')



def appl_rate_bar(application_rates_path):
    df_feb = pd.read_excel(application_rates_path, sheet_name='2025FEB')
    df_jul = pd.read_excel(application_rates_path, sheet_name='2025JUL')

    room_types = ['3R','4R','5R']

    for room in room_types:
        st.subheader(f"{room} Application Rate for First-Timers")

        # Prepare bar chart
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Bar: FEB Count
        fig.add_trace(go.Bar(
            x = df_feb['Town'],
            y = df_feb[f'{room} Count'],
            name = '2025FEB Count',
            marker_color='#854745'
        ), secondary_y=False)

        # Bar: JUL Count
        fig.add_trace(go.Bar(
            x = df_jul['Town'],
            y = df_jul[f'{room} Count'],
            name = '2025JUL Count',
            marker_color='#27718f'
        ), secondary_y=False)

        # Line: FEB Rate
        fig.add_trace(go.Scatter(
            x = df_feb['Town'],
            y = df_feb[f'{room} Rate'],
            name = '2025FEB Rate',
            mode='lines+markers',
            line=dict(color='darkred', dash='dot')
        ), secondary_y=True)

        # Line: JUL Rate
        fig.add_trace(go.Scatter(
            y = df_jul[f'{room} Rate'],
            x = df_jul['Town'],
            name = '2025JUL Rate',
            mode='lines+markers',
            line=dict(color='steelblue', dash='dot')
        ), secondary_y=True)


        # Layout setup
        fig.update_layout(
            title = f"{room} - Counts (bars) & Rates (lines)",
            xaxis_title='Town',
            yaxis_title='SBF Unit Count',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            height=600,
            barmode='group'
        )

        # Right Y-Axis label
        fig.update_yaxes(title_text="Application Rate", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)









