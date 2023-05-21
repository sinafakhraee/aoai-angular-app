import { Component } from '@angular/core';

@Component({
    selector: 'app-footer',
    template: `
        <div class="layout-footer">
            <div>
                <!-- <span>Azure OpenAI</span> -->
                <a href="https://azure.microsoft.com/en-us/products/cognitive-services/openai-service/">Azure OpenAI</a>
            </div>
        </div>
    `
})
export class AppFooterComponent {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    version = require('package.json') && require('package.json').version;
}
