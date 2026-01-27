import { Component } from '@angular/core';
import { PageHeaderComponent } from '../../../../shared/components/page-header/page-header.component';

@Component({
  selector: 'app-diagram',
  standalone: true,
  imports: [PageHeaderComponent],
  templateUrl: './diagram.component.html',
})
export class DiagramComponent {}
