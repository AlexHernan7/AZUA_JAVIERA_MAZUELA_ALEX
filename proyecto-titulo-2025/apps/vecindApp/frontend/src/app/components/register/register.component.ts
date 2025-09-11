import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';


@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule,HttpClientModule, FormsModule], 
  templateUrl: './register.component.html',
  styleUrl: './register.component.css',
})
export class RegisterComponent implements OnInit  {

  regiones: string[] = [];
  comunas: string[] = [];
  regionesComunas: Record<string, string[]> = {};
   regionSeleccionada = '';
  comunaSeleccionada = '';

   constructor(private router: Router, private http: HttpClient) {}
   photoPreview: string | null = null;

   ngOnInit(): void {
    // Carga el JSON con regiones y comunas
    this.http
      .get<Record<string, string[]>>('/data/regiones-comunas.json')
      .subscribe((data) => {
        this.regionesComunas = data;
        this.regiones = Object.keys(data).sort(); // opcional: orden alfabético
      });}

onFileChange(evt: Event) {
    const input = evt.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => (this.photoPreview = reader.result as string);
    reader.readAsDataURL(file);}

    onRegionChange(event: Event) {
  const target = event.target as HTMLSelectElement;
  const region = target.value;
  this.regionSeleccionada = region;
  this.comunas = this.regionesComunas[region] ?? [];
  this.comunaSeleccionada = '';
}
  }
  
  

