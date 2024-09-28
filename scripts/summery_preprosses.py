import pandas as pd
import matplotlib.pyplot as plt

# Load the preprocessed data
df = pd.read_csv('preprocessed_data.csv')

# Summary calculations
total_messages = df.shape[0]
total_tokens = df[[col for col in df.columns if 'token_' in col]].count().sum()
average_tokens_per_message = df[[col for col in df.columns if 'token_' in col]].count().mean()

# Create summary data
summary = {
    'Total Messages': total_messages,
    'Total Tokens': total_tokens,
    'Average Tokens per Message': average_tokens_per_message
}

# Create a DataFrame for the summary
summary_df = pd.DataFrame(summary, index=[0])

# Print the summary table
print(summary_df)

# Plotting the summary table as an image
fig, ax = plt.subplots()
ax.axis('tight')
ax.axis('off')
table_data = summary_df.values.tolist()
table = ax.table(cellText=table_data, colLabels=summary_df.columns, cellLoc='center', loc='center')

# Save the table as a JPG image
plt.savefig('summary_table.jpg', bbox_inches='tight', pad_inches=0.1, dpi=300)

# Show the plot (optional)
plt.show()
