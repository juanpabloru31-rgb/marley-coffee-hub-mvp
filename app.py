import streamlit as st
from datetime import datetime, timedelta
import json

st.set_page_config(page_title='Marley Coffee | Hub B2B · Demo', page_icon='☕', layout='wide')
st.markdown('''<style>.stApp{background:#F5F3EF;color:#241C18}h1,h2,h3{color:#241C18}div.stButton>button[kind="primary"]{background:#3E2723;color:white;border:0} .stMetric{background:#fff;padding:12px;border-radius:12px}</style>''', unsafe_allow_html=True)

PRODUCTS = {'Café en grano 1 kg': 18900, 'Café molido 500 g': 10900, 'Cápsulas (caja)': 8900}
MACHINES = [
    {'id':'EQ-101','sede':'Oficina central','area':'Área de colaboradores','marca':'JURA','modelo':'WE8','tipo':'Oficina','estado':'Operativo'},
    {'id':'EQ-102','sede':'Oficina central','area':'Sala de reuniones','marca':'Saeco','modelo':'Magic M2','tipo':'Oficina','estado':'Requiere revisión'},
    {'id':'EQ-103','sede':'Sucursal comercial','area':'Recepción de clientes','marca':'JURA','modelo':'W8','tipo':'Oficina','estado':'Operativo'},
    {'id':'EQ-104','sede':'Panadería asociada','area':'Zona de atención','marca':'Necta','modelo':'Krea Touch','tipo':'Otro canal / referencia','estado':'Operativo'},
    {'id':'EQ-105','sede':'Cafetería asociada','area':'Barra de servicio','marca':'Saeco','modelo':'Magic M2','tipo':'Otro canal / referencia','estado':'Requiere revisión'},
]

def machine_label(m):
    return f"{m['id']} · {m['marca']} {m['modelo']} — {m['sede']} / {m['area']}"

def incident_plan(kind):
    plans={
      'No dispensa café':('Posible obstrucción, falta de suministro o problema del grupo dispensador.', 'Comprobar suministro de agua y café; revisar avisos del panel; coordinar diagnóstico técnico.'),
      'No enciende':('Posible problema de alimentación eléctrica o sistema de encendido.', 'Verificar alimentación externa segura y coordinar revisión eléctrica con técnico autorizado.'),
      'Fuga de agua':('Posible fuga en conexiones, depósito o circuito hidráulico.', 'Dejar de usar el equipo y solicitar revisión técnica. No manipular componentes internos.'),
      'Café sale frío':('Posible falla de calentamiento o configuración.', 'Revisar avisos del panel y coordinar evaluación del sistema de temperatura.'),
      'Error en pantalla':('Código de error pendiente de interpretación.', 'Registrar código visible y derivar a servicio técnico para diagnóstico.'),
      'Mantenimiento preventivo':('Solicitud programada de revisión y limpieza profesional.', 'Coordinar disponibilidad de visita y revisión de mantenimiento.'),
      'Otro':('La causa no puede determinarse con la información inicial.', 'Revisar descripción y solicitar antecedentes adicionales antes de asignar una visita.'),
    }
    return plans.get(kind,plans['Otro'])


def init():
    defaults = {'role':None,'page':'Inicio','cart':{},'cart_version':0,'last_order_id':None,'checkout_delivery':'Despacho a domicilio (simulado)','orders':[{'id':'PED-001','fecha':'2026-09-12','detalle':'Café en grano 1 kg × 4','estado':'Entregado'}], 'selected_machine':'EQ-101','last_ticket_id':None,'tickets':[{'id':'OCS-001','equipo':machine_label(MACHINES[0]),'detalle':'Revisión preventiva (ejemplo)','estado':'Cerrado'}]}
    for key,val in defaults.items():
        if key not in st.session_state: st.session_state[key]=val
init()

st.caption('PROTOTIPO ACADÉMICO · DATOS FICTICIOS · SIN CONEXIÓN A MARLEY COFFEE NI DICALLA SPA')
st.title('☕ Marley Coffee | Hub de Autogestión B2B')
st.write('Demostración funcional de portal web responsive para HORECA y OCS.')

if st.session_state.role is None:
    st.subheader('Acceso de demostración')
    with st.form('login'):
        role = st.selectbox('Perfil de cliente', ['HORECA — Restaurante / cafetería', 'OCS — Oficina / empresa'])
        company = st.text_input('Empresa (ficticia)', value='Cliente de demostración')
        st.caption('No ingreses RUT ni contraseñas reales. Este acceso es solo una simulación.')
        submit=st.form_submit_button('Ingresar al portal', type='primary')
    if submit:
        st.session_state.role='HORECA' if role.startswith('HORECA') else 'OCS'
        st.session_state.company=company
        st.session_state.page='Inicio'
        st.rerun()
    st.stop()

with st.sidebar:
    st.subheader(st.session_state.company)
    st.caption('Perfil: '+st.session_state.role)
    menu = ['Inicio','Reposición','Confirmación','Historial'] if st.session_state.role=='HORECA' else ['Inicio','Mis equipos','Reportar falla','Seguimiento']
    page=st.radio('Navegación', menu, index=menu.index(st.session_state.page) if st.session_state.page in menu else 0)
    st.session_state.page=page
    if st.button('Cerrar sesión'):
        st.session_state.role=None
        st.session_state.page='Inicio'
        st.rerun()

role=st.session_state.role
page=st.session_state.page
if role=='HORECA':
    if page=='Inicio':
        st.header('Dashboard HORECA')
        a,b,c=st.columns(3)
        a.metric('Pedidos de ejemplo',len(st.session_state.orders))
        b.metric('Productos disponibles',len(PRODUCTS))
        c.metric('Carrito actual',sum(st.session_state.cart.values()))
        st.info('Este panel simula el acceso a reposición e historial del cliente empresa.')
        if st.button('Ir a reposición',type='primary'):
            st.session_state.page='Reposición';st.rerun()
    elif page=='Reposición':
        st.header('Reposición HORECA')
        st.write('Modifica cantidades y confirma un pedido de prueba. No se realizará ninguna compra real.')
        st.caption('Los importes se recalculan automáticamente al cambiar cualquier cantidad.')
        qty = {}
        for i, (product, price) in enumerate(PRODUCTS.items()):
            qty[product] = st.number_input(
                f'{product} · Precio ficticio ${price:,.0f} CLP'.replace(',', '.'),
                min_value=0, max_value=100,
                value=st.session_state.cart.get(product, 0),
                step=1, key=f'auto_qty_{st.session_state.cart_version}_{i}',
            )
        # Los controles están fuera de st.form: cada cambio dispara un rerun.
        # Solo se lee su valor y se calcula el total, sin modificar sus claves.
        st.session_state.cart = qty.copy()
        total = sum(PRODUCTS[p] * q for p, q in qty.items())
        st.subheader('Resumen del carrito')
        for p, q in qty.items():
            if q:
                subtotal = PRODUCTS[p] * q
                st.write(f'{p}: {q} × ${PRODUCTS[p]:,.0f} = ${subtotal:,.0f}'.replace(',', '.'))
        if not total:
            st.info('Agrega productos con el botón + para ver el total.')
        st.metric('Total ilustrativo (CLP)', f'${total:,.0f}'.replace(',', '.'))
        st.divider()
        st.subheader('Entrega y condiciones del pedido')
        delivery = st.radio('Modalidad de entrega', ['Despacho a domicilio (simulado)', 'Retiro en punto habilitado (simulado)'], key='checkout_delivery')
        st.caption('Los plazos son ejemplos académicos: no representan disponibilidad ni compromisos reales de Marley Coffee.')
        if delivery.startswith('Despacho'):
            st.info('Entrega estimada ficticia: 2 a 4 días hábiles desde la confirmación. El horario exacto requeriría coordinación logística real.')
        else:
            st.info('Retiro ilustrativo: sujeto a preparación y confirmación del punto de retiro. No se ha habilitado ningún local real.')
        if st.button('Confirmar pedido simulado',type='primary',disabled=total==0):
            now=datetime.now()
            items=[{'producto':p,'cantidad':q,'precio_unitario':PRODUCTS[p],'subtotal':PRODUCTS[p]*q} for p,q in qty.items() if q]
            order_id=f'PED-{len(st.session_state.orders)+1:03d}'
            eta=now+timedelta(days=3 if delivery.startswith('Despacho') else 1)
            order={'id':order_id,'fecha':now.strftime('%Y-%m-%d %H:%M'), 'empresa':st.session_state.company,
                   'detalle':', '.join(f'{x["producto"]} × {x["cantidad"]}' for x in items),
                   'estado':'Pedido recibido (simulado)', 'items':items,'total':total,
                   'entrega':delivery,'estimacion':eta.strftime('%d-%m-%Y'),
                   'convenio':'Condiciones comerciales ficticias de demostración',
                   'documento':'Comprobante de demostración — NO es factura tributaria'}
            st.session_state.orders.insert(0,order)
            st.session_state.last_order_id=order_id
            st.session_state.cart={}
            st.session_state.cart_version+=1
            st.session_state.page='Confirmación'
            st.rerun()
    elif page=='Confirmación':
        st.header('Pedido confirmado · Demostración')
        order=next((o for o in st.session_state.orders if o['id']==st.session_state.last_order_id),None)
        if not order or 'items' not in order:
            st.info('Todavía no hay un pedido nuevo confirmado en esta sesión. Realiza una reposición para ver el comprobante.')
        else:
            st.success(f'Pedido {order["id"]} registrado correctamente en esta sesión de prueba.')
            a,b,c=st.columns(3)
            a.metric('Número de pedido',order['id'])
            b.metric('Total simulado',f'${order["total"]:,.0f}'.replace(',','.'))
            c.metric('Estado','Recibido')
            st.subheader('Comprobante de pedido — NO es factura tributaria')
            st.write('**Cliente empresa:**',order['empresa'])
            st.write('**Fecha y hora de registro:**',order['fecha'])
            st.write('**Convenio:**',order['convenio'])
            st.write('**Entrega seleccionada:**',order['entrega'])
            st.write('**Fecha referencial de entrega o retiro:**',order['estimacion'])
            st.caption('Fecha ficticia calculada para demostrar el flujo; no existe coordinación logística ni hora comprometida.')
            st.dataframe(order['items'],use_container_width=True,hide_index=True,
                         column_config={'producto':'Producto','cantidad':'Cantidad','precio_unitario':st.column_config.NumberColumn('Precio unitario (CLP)',format='$%d'),'subtotal':st.column_config.NumberColumn('Subtotal (CLP)',format='$%d')})
            st.subheader('Seguimiento y postventa (simulados)')
            st.write('① Pedido recibido → ② Preparación pendiente → ③ Despacho/retiro pendiente → ④ Entrega pendiente')
            st.info('En esta demostración el pedido queda en estado «Recibido». Los siguientes estados no se actualizan mediante una operación real.')
            receipt={'aviso':'DOCUMENTO DEMOSTRATIVO - NO ES FACTURA TRIBUTARIA',**order}
            st.download_button('Descargar comprobante de prueba (JSON)',data=json.dumps(receipt,ensure_ascii=False,indent=2),
                               file_name=f'{order["id"]}_demo.json',mime='application/json')
            if st.button('Volver a reposición'):
                st.session_state.page='Reposición';st.rerun()
    else:
        st.header('Historial de pedidos')
        st.dataframe([{k:o.get(k,'—') for k in ('id','fecha','detalle','estado','total','estimacion')} for o in st.session_state.orders],use_container_width=True,hide_index=True)
        st.caption('Los documentos contables y facturas tributarias reales requieren integración y emisión autorizada. Los pedidos nuevos son temporales y simulados.')
        if st.session_state.last_order_id and st.button('Ver comprobante del último pedido'):
            st.session_state.page='Confirmación';st.rerun()
else:
    def select_machine(mid):
        st.session_state.selected_machine=mid
        st.session_state.page='Reportar falla'
        st.rerun()

    def equipment_cards():
        st.caption('Inventario ilustrativo con modelos comerciales reales y ubicaciones ficticias. No hay telemetría ni conexión a equipos.')
        for m in MACHINES:
            with st.container(border=True):
                left,right=st.columns([3,1])
                with left:
                    st.subheader('☕ '+m['marca']+' '+m['modelo'])
                    st.write(f"**Código:** {m['id']} · **Ubicación:** {m['sede']} — {m['area']}")
                    st.write(f"**Canal de referencia:** {m['tipo']} · **Estado registrado:** {m['estado']}")
                with right:
                    if st.button('Ver y reportar',key='choose_'+m['id'],type='primary'):
                        select_machine(m['id'])

    if page=='Inicio':
        st.header('Panel de servicio y soporte')
        st.write(f"Empresa: **{st.session_state.company}**")
        a,b,c=st.columns(3)
        a.metric('Equipos asociados (demo)',len(MACHINES))
        b.metric('Tickets registrados',len(st.session_state.tickets))
        c.metric('Meta de respuesta OCS','< 18 h')
        st.info('Selecciona una máquina para consultar su ficha y reportar una incidencia.')
        equipment_cards()
    elif page=='Mis equipos':
        st.header('Mis equipos y ubicaciones')
        equipment_cards()
    elif page=='Reportar falla':
        st.header('Nueva solicitud de servicio técnico')
        ids=[m['id'] for m in MACHINES]
        current=st.session_state.selected_machine if st.session_state.selected_machine in ids else ids[0]
        chosen=st.selectbox('Equipo asociado a tu empresa',ids,index=ids.index(current),format_func=lambda x:machine_label(next(m for m in MACHINES if m['id']==x)))
        st.session_state.selected_machine=chosen
        m=next(m for m in MACHINES if m['id']==chosen)
        with st.container(border=True):
            st.write(f"**Marca y modelo:** {m['marca']} {m['modelo']}")
            st.write(f"**Identificador:** {m['id']} · **Sede:** {m['sede']} · **Área:** {m['area']}")
            st.write(f"**Estado previo registrado:** {m['estado']}")
        with st.form('ocs_incident_form',clear_on_submit=False):
            problem=st.selectbox('Tipo de incidencia',['No dispensa café','No enciende','Fuga de agua','Café sale frío','Error en pantalla','Mantenimiento preventivo','Otro'])
            severity=st.selectbox('Impacto en la operación',['Servicio parcialmente disponible','Equipo fuera de servicio','Solicitud preventiva / sin interrupción'])
            detail=st.text_area('¿Qué está ocurriendo? Describe los síntomas (sin datos personales)',placeholder='Ej.: Desde esta mañana el equipo enciende, pero no entrega café y muestra una alerta en pantalla.')
            st.caption('La evaluación técnica y los tiempos se muestran como un flujo propuesto, no como un compromiso real.')
            send=st.form_submit_button('Registrar incidencia y generar ticket',type='primary')
        if send:
            if len(detail.strip())<12:
                st.warning('Describe la falla con al menos 12 caracteres para generar un ticket útil.')
            else:
                now=datetime.now()
                code=f'OCS-{len(st.session_state.tickets)+1:03d}'
                diagnosis,action=incident_plan(problem)
                ticket={'id':code,'empresa':st.session_state.company,'equipo':machine_label(m),'equipo_id':chosen,'marca':m['marca'],'modelo':m['modelo'],'sede':m['sede'],'area':m['area'],
                        'tipo':problem,'impacto':severity,'detalle':detail.strip(),'fecha':now.strftime('%d-%m-%Y %H:%M'),
                        'estado':'Solicitud recibida','responsable':'Mesa de soporte — asignación pendiente (simulada)',
                        'diagnostico':diagnosis,'accion':action,'meta_primera_respuesta':(now+timedelta(hours=2)).strftime('%d-%m-%Y %H:%M'),
                        'meta_atencion':(now+timedelta(hours=18)).strftime('%d-%m-%Y %H:%M'),
                        'etapa':0}
                st.session_state.tickets.insert(0,ticket)
                st.session_state.last_ticket_id=code
                st.session_state.page='Seguimiento'
                st.rerun()
    elif page=='Seguimiento':
        st.header('Seguimiento de solicitudes técnicas')
        tickets=st.session_state.tickets
        options=[t['id'] for t in tickets]
        preferred=st.session_state.last_ticket_id if st.session_state.last_ticket_id in options else options[0]
        ticket_id=st.selectbox('Selecciona un ticket',options,index=options.index(preferred))
        t=next(t for t in tickets if t['id']==ticket_id)
        if t.get('tipo'):
            st.success(f"Solicitud {t['id']} registrada para {t['empresa']}. Puedes revisar el detalle y las próximas acciones.")
            a,b,c=st.columns(3)
            a.metric('Ticket',t['id'])
            b.metric('Estado',t['estado'])
            c.metric('Meta de atención propuesta','< 18 h')
            st.subheader('Detalle de la incidencia')
            st.write(f"**Empresa:** {t['empresa']} · **Fecha y hora:** {t['fecha']}")
            st.write(f"**Equipo:** {t['marca']} {t['modelo']} ({t['equipo_id']})")
            st.write(f"**Ubicación:** {t['sede']} — {t['area']}")
            st.write(f"**Falla reportada:** {t['tipo']} · **Impacto:** {t['impacto']}")
            st.write(f"**Descripción del cliente:** {t['detalle']}")
            st.write(f"**Diagnóstico preliminar orientativo:** {t['diagnostico']}")
            st.write(f"**Plan inicial de atención:** {t['accion']}")
            st.write(f"**Área responsable:** {t['responsable']}")
            st.subheader('Compromisos de demostración y trazabilidad')
            st.write(f"**Primera respuesta objetivo (ejemplo):** {t['meta_primera_respuesta']}")
            st.write(f"**Meta de atención (ejemplo):** {t['meta_atencion']}")
            st.caption('La meta <18 h es un KPI del proyecto, no una reparación garantizada. El despacho de técnicos depende de validación, cobertura, disponibilidad y acuerdos de servicio.')
            stages=['Solicitud recibida','Clasificación y diagnóstico','Asignación técnica','Visita o asistencia','Cierre y conformidad']
            for i,label in enumerate(stages):
                st.write(('✅ ' if i<=t['etapa'] else '○ ')+label)
            with st.expander('Simular avance de estado (solo para exposición)'):
                if st.button('Avanzar una etapa',disabled=t['etapa']>=len(stages)-1):
                    t['etapa']+=1
                    t['estado']=stages[t['etapa']]
                    st.rerun()
            st.download_button('Descargar constancia del ticket (JSON)',data=json.dumps({'advertencia':'Documento de demostración; no corresponde a un servicio real',**t},ensure_ascii=False,indent=2),file_name=f'{t["id"]}_demo.json',mime='application/json')
        else:
            st.info('Este es un ticket histórico de ejemplo. Crea uno nuevo para visualizar el seguimiento completo.')
            st.write(t)
        st.divider()
        st.subheader('Historial de tickets')
        st.dataframe([{'Ticket':x['id'],'Equipo':x['equipo'],'Estado':x['estado'],'Fecha':x.get('fecha','—')} for x in tickets],hide_index=True,use_container_width=True)
        st.caption('Todos los tickets y cambios de estado son temporales: se pierden al reiniciar la sesión.')

st.divider()
st.caption('Proyecto académico · Duoc UC · Marley Coffee / Dicalla SpA (caso de estudio). MVP de demostración, no servicio oficial.')
