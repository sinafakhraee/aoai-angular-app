import { Component, Input } from '@angular/core';
import { MessageService } from 'primeng/api';
import { Code } from '../../domain/code';
import { Injectable } from '@angular/core';
import { HttpClient, HttpEventType, HttpHeaders } from '@angular/common/http';
import { ProgressBarModule } from 'primeng/progressbar';
import { FileUpload } from 'primeng/fileupload';
import { PanelModule } from 'primeng/panel';
import { Panel } from 'primeng/panel';
import { InputTextModule } from 'primeng/inputtext';
import { saveAs } from 'file-saver';

@Component({
    selector: 'file-upload-basic-demo',
    template: ` <section>
        <app-docsectiontext [title]="title" [id]="id">
            <p>Upload your document to analyze using Azure OpenAI.</p>
        </app-docsectiontext>
        <div class="card flex justify-content-center">
            <p-toast></p-toast>
            <p-fileUpload
                [disabled]="uploading"
                mode="basic"
                (onBeforeUpload)="onBeforeUpload($event)"
                chooseLabel="Choose"
                name="demo[]"
                accept=".pdf"
                url="https://www.primefaces.org/cdn/api/upload.php"
                maxFileSize="60000000"
                (onUpload)="onUpload($event)"
                (onSelect)="onSelect($event)"
            >
            </p-fileUpload>
        </div>

        <div class="card" *ngIf="showProgressBar">
            <p-progressBar mode="indeterminate" [style]="{ height: '6px' }"></p-progressBar>
            <div class="progress-bar-label" [style]="{ color: 'red', fontSize: '18px' }">Your file is being uploaded</div>
        </div>
        <div>
            <p-table [value]="myFile" [tableStyle]="{ 'min-width': '50rem' }">
                <ng-template pTemplate="header">
                    <tr>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Size</th>
                    </tr>
                </ng-template>
                <ng-template pTemplate="body" let-file>
                    <tr>
                        <td>{{ file.Name }}</td>
                        <td>{{ file.Type }}</td>
                        <td>{{ file.Size }}</td>
                    </tr>
                </ng-template>
            </p-table>
        </div>
        <div class="card flex justify-content-left">
            <p-button (click)="fetchData()" label="Summarize" [disabled]="summerizeDisabled"></p-button>
        </div>
        <div class="card" *ngIf="isLoading">
            <p-progressBar mode="indeterminate" [style]="{ height: '6px' }"></p-progressBar>
            <div class="progress-bar-label" [style]="{ color: 'red', fontSize: '18px' }">Your document is being summarized...</div>
        </div>
        <div>
            <div style="margin-top: 1rem; display: flex; flex-direction: column;" *ngIf="result">
                <p-panel [header]="'Summary'">
                    <p>{{ result}}</p>
                </p-panel>
            </div>
        </div>

        <div class="card flex justify-content-left">
            <div style="display: flex; align-items: center; width: 100%;">
                <input pInputText type="text" placeholder="ask anything and we'll search your document" [(ngModel)]="question" style="width: 90%; margin-right: 10px;" />

                <p-button (click)="search()" label="Search..."></p-button>
            </div>
        </div>
        <div>
            <div style="margin-top: 1rem; display: flex; flex-direction: column;">
                <p-panel [header]="'Answer'">
                    <p style="color: blue;">{{ displayedAnswer}}</p>
                    <!-- Reference: <a [href]="source" target="_blank" rel="noopener noreferrer" style="text-decoration: underline;">{{ source }}</a> -->
                    Reference: <a href="javascript:void(0);" (click)="downloadFile()" style="text-decoration: underline;">{{ source }}</a>
                </p-panel>
                
            </div>
        </div>
        
        <app-code selector="file-upload-basic-demo"></app-code>
    </section>`,
    providers: [MessageService]
})
export class BasicDoc {
    @Input() id: string;

    @Input() title: string;
    myFile: any[];
    summerizeDisabled: boolean = true;
    showProgressBar = false;
    uploading = false;
    progress: number = 0;
    result: string;
    answer: string;
    source_: string;
    source: string;
    isLoading: boolean = false;
    question: string;
    displayedAnswer: string;
    
    constructor(private messageService: MessageService, private http: HttpClient) {}

    private apiUrl = 'http://127.0.0.1:5000/upload_local';

    private summerizeUrl = 'http://127.0.0.1:5000/summarize_from_local';

    private q_and_a_URL = 'http://127.0.0.1:5000/q_and_a';

    // ...
    downloadFile() {
        
        let temp = this.source.split('\\').pop();
        temp = temp.replace('.pdf', '').replace(':', '_page_') + '.pdf';
        
        const fileName = temp;
        console.log("fileName:" + fileName)
        const downloadUrl = `http://localhost:5000/download/${fileName}`;  // Replace with your API endpoint
      
        this.http.get(downloadUrl, { responseType: 'blob' }).subscribe((data: Blob) => {
          saveAs(data, fileName);
        });
    }



    displayAnswer() {
        this.displayedAnswer = '';
        let i = 0;
        const delay = 10; // you can adjust the delay (in ms) to your preference
    
        const displayOneByOne = () => {
          if (i < this.answer.length) {
            this.displayedAnswer += this.answer.charAt(i);
            i++;
            setTimeout(displayOneByOne, delay);
          }
        };
    
        displayOneByOne();
        this.source = this.source_
      }







    search() {
        console.log('entered search');
        const requestBody = {
            question: this.question
        };
        // const headers = new HttpHeaders({ 'Content-Type': 'application/json' });

        this.http.post<{ output_text: string, source: string }>(this.q_and_a_URL, requestBody).subscribe(
            (response) => {
                console.log('response');
                console.log(response);                        
                // this.answer = response;
                this.answer = response.output_text;
                this.source_ = response.source
                this.displayAnswer();
                
            },
            (error) => {
                console.error(error);
            }
        );
    }

    fetchData() {
        this.result = '';
        this.isLoading = true;
        this.http.get<string>(this.summerizeUrl).subscribe(
            (response) => {
                const responseObj = response as any;
                console.log(response);
                this.result = responseObj[0].summary;                            
                this.isLoading = false;
            },
            (error) => {
                console.error(error);
                this.isLoading = false;
            }
        );
    }

    onBeforeUpload(event: any) {
        console.log('Upload button clicked:', event);
        this.showProgressBar = true;
        this.uploading = true;
    }
    onSelect(event: any) {
        console.log('Selected files:', event.files);
        this.summerizeDisabled = true;
        this.result = '';
    }
    uploadFile(file: File) {
        const formData: FormData = new FormData();
        formData.append('file', file, file.name);

        return this.http.post(this.apiUrl, formData);
    }
    //   async onUpload(event:{ files: File[]}) {
    async onUpload(event: any) {
        this.myFile = [{ Name: event.files[0].name, Type: event.files[0].type, Size: event.files[0].size }];
        console.log('event.selectedFile');
        this.uploadFile(event.files[0]).subscribe(
            (response) => {
                console.log('Upload successful:', response);
            },
            (error) => {
                console.error('Upload failed:', error);
            }
        );
        this.uploading = false;
        this.showProgressBar = false;
        this.summerizeDisabled = false;
        this.messageService.add({ severity: 'info', summary: 'Success', detail: 'File Uploaded with Basic Mode' });
    }

    code: Code = {
        basic: `
<p-fileUpload mode="basic" chooseLabel="Choose" name="demo[]" url="https://www.primefaces.org/cdn/api/upload.php" accept="image/*" maxFileSize="1000000" (onUpload)="onUpload($event)"></p-fileUpload>`,
        html: `
<div class="card flex justify-content-center">
    <p-toast></p-toast>
    <p-fileUpload mode="basic" chooseLabel="Choose" name="demo[]" url="https://www.primefaces.org/cdn/api/upload.php" accept="image/*" maxFileSize="1000000" (onUpload)="onUpload($event)"></p-fileUpload>
</div>`,
        typescript: `
import { Component } from '@angular/core';
import { MessageService } from 'primeng/api';

@Component({
    selector: 'file-upload-basic-demo',
    templateUrl: './file-upload-basic-demo.html',
    providers: [MessageService]
})
export class FileUploadBasicDemo {
    constructor(private messageService: MessageService) {}

    onUpload(event) {
        this.messageService.add({ severity: 'info', summary: 'Success', detail: 'File Uploaded with Basic Mode' });
    }
}`
    };
}
