import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LogoComponent } from '../../../../shared/components/logo/logo.component';
import { GithubButtonComponent } from '../../../../shared/components/github-button/github-button.component';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [CommonModule, LogoComponent, GithubButtonComponent],
  templateUrl: './footer.component.html',
})
export class FooterComponent {}
