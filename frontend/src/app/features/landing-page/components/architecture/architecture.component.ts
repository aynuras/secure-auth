import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PageHeaderComponent } from '../../../../shared/components/page-header/page-header.component';

@Component({
  selector: 'app-architecture',
  standalone: true,
  imports: [CommonModule, PageHeaderComponent],
  templateUrl: './architecture.component.html',
  styleUrls: ['./architecture.component.css'],
})
export class ArchitectureComponent {
}
