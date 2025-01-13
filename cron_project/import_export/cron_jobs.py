from django_cron import CronJobBase, Schedule
import csv

class FileProcessingCronJob(CronJobBase):
    RUN_EVERY_MINS = 60
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'import_export.file_processing_cron_job'

    def do(self):
        print("Cron job started.")
        #change the path
        file_path = "C:/Users/User/Downloads/KayakTransactionReport.csv"
        output_file = "C:/Users/User/Downloads/ProcessedReport.csv"

        try:
            print(f"Processing file at: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                # Update fieldnames to include the 'Processed' field
                fieldnames = reader.fieldnames + ['Processed']

                with open(output_file, 'w', encoding='utf-8', newline='') as out_file:
                    writer = csv.DictWriter(out_file, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for row in reader:
                        # Add the 'Processed' field
                        row['Processed'] = True
                        writer.writerow(row)

            print(f"Processed data saved to {output_file}")
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error processing file: {e}")
